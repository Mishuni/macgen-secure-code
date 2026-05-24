"""
Model factory for chat LLMs (OpenAI, Gemini, Anthropic Claude, DeepSeek via Ollama).

Usage:
    from ours.llm import create_chat_model
    llm = create_chat_model("gpt4o-mini", temperature=0.2)

Notes:
- Keeps third‑party imports narrow and optional where possible (Gemini).
- For DeepSeek (local) we wrap outputs to strip <think>…</think> segments.
"""

from typing import Optional, Any

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

# Optional import for Gemini: keep soft dependency
try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    from google.generativeai.types import HarmCategory, HarmBlockThreshold  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None  # type: ignore
    HarmCategory = None  # type: ignore
    HarmBlockThreshold = None  # type: ignore

# Optional import for Anthropic Claude: keep soft dependency
try:
    from langchain_anthropic import ChatAnthropic  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ChatAnthropic = None  # type: ignore

from macgen.utils.text import strip_think_tags, to_text
from macgen.config import model_mapping
from macgen.utils.callbacks import TokenUsageCallback

__all__ = ["create_chat_model", "get_gemini_safety_settings"]


def get_gemini_safety_settings() -> Optional[dict]:
    """Return permissive Gemini safety settings if the dependency is present.
    If the google genai types are not available, returns None.
    """
    if HarmCategory is None or HarmBlockThreshold is None:
        return None
    return {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    }


def _wrap_sanitize() -> RunnableLambda:
    """Return a Runnable that removes null bytes / invalid unicode from LLM output.
    Prevents openai.BadRequestError (400) when output is fed into the next chain.
    """

    def _sanitize(msg: Any) -> AIMessage:
        content = to_text(msg).replace('\x00', '').encode('utf-8', errors='ignore').decode('utf-8')
        return AIMessage(content=content)

    return RunnableLambda(_sanitize)


def _wrap_strip_think() -> RunnableLambda:
    """Return a Runnable that strips <think> blocks from AIMessage/content."""

    def _strip(msg: Any) -> AIMessage:
        # Normalize to string then strip hidden reasoning blocks
        return AIMessage(content=strip_think_tags(to_text(msg)))

    return RunnableLambda(_strip)


def _wrap_truncate(max_chars: int = 8000) -> RunnableLambda:
    """Return a Runnable that truncates content if too long (for qwen)."""

    def _truncate(msg: Any) -> AIMessage:
        content = to_text(msg)
        if len(content) > max_chars:
            content = content[-max_chars:] + "\n"
        return AIMessage(content=content)

    return RunnableLambda(_truncate)


def create_chat_model(
    model_name: str,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    coder: bool = False,
    agent_name: str = "generic",
):
    """Create a LangChain chat model based on a friendly model_name."""
    if not model_name:
        raise ValueError("model_name must be provided")

    # normalize
    mn = str(model_name).lower()

    # 1) DeepSeek / Qwen via Ollama (local models)
    if mn.startswith(("deepseek", "qwen")):
        resolved = model_mapping[model_name]
        # Bound generation length to prevent runaway / near-infinite outputs.
        # If max_tokens isn't provided by the caller, use a conservative default.
        default_num_predict = 4096 if coder else 4096
        num_predict = int(max_tokens) if max_tokens is not None else default_num_predict

        # keep_alive=-1: keep model loaded in memory (reduces reload latency)
        # timeout=600: guard against cases where qwen stalls/repeats for a long time
        ollama_kwargs: dict[str, Any] = {
            "model": resolved,
            "temperature": temperature,
            "keep_alive": -1,
        }
        if mn.startswith("qwen") or "qwen" in str(resolved).lower():
            ollama_kwargs["timeout"] = 600
            ollama_kwargs["num_predict"] = 100000
            # ollama_kwargs["think"] = False

        model = ChatOllama(**ollama_kwargs)
        # Pipe through a cleanup runnable that strips <think> blocks
        chain = model | _wrap_strip_think() | _wrap_sanitize()
        # Qwen only: truncate if too long
        if mn.startswith("qwen"):
            chain = chain | _wrap_truncate(max_chars=5000)
        return chain

    # 2) Gemini (Google) — soft dependency
    if mn.startswith(("gemini", "google")):
        if ChatGoogleGenerativeAI is None:
            raise RuntimeError(
                "langchain-google-genai is not installed; install it to use Gemini models."
            )
        safety = get_gemini_safety_settings()
        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "max_output_tokens": None,
            "convert_system_message_to_human": True,
        }
        if safety is not None:
            kwargs["safety_settings"] = safety
        return ChatGoogleGenerativeAI(**kwargs) | _wrap_sanitize()

    # 3) Anthropic Claude — soft dependency
    if mn.startswith(("claude", "anthropic")):
        if ChatAnthropic is None:
            raise RuntimeError(
                "langchain-anthropic is not installed; install it to use Claude models."
            )
        resolved = model_mapping.get(model_name, model_name)
        callback = TokenUsageCallback(model_name=model_name, agent_name=agent_name)
        kwargs = {
            "model": resolved,
            "temperature": temperature,
            "max_tokens": max_tokens if max_tokens is not None else 4096,
            "callbacks": [callback],
        }
        return ChatAnthropic(**kwargs) | _wrap_sanitize()

    # 4) OpenAI (default)

    resolved = model_mapping[model_name]

    # return ChatOpenAI(model=resolved, temperature=temperature, max_tokens=max_tokens)
    callback = TokenUsageCallback(model_name=model_name, agent_name=agent_name)
    callbacks = [callback]

    if "gpt-5" in resolved:
        params = {"model": resolved, "callbacks": callbacks}
        params["temperature"] = 1.0
        # params["max_completion_tokens"] = max_tokens
        return ChatOpenAI(**params) | _wrap_sanitize()

    return ChatOpenAI(
        model=resolved,
        temperature=temperature,
        max_tokens=max_tokens,
        callbacks=callbacks,
    ) | _wrap_sanitize()
