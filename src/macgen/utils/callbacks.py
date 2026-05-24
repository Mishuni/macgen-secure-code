from __future__ import annotations
from typing import Any, Dict

from langchain_core.callbacks import BaseCallbackHandler
from .usage import global_usage_tracker, get_current_phase


def _extract_usage_dict(response: Any) -> Dict[str, Any]:
    usage = getattr(response, "usage_metadata", None)
    if isinstance(usage, dict):
        return usage

    llm_output = getattr(response, "llm_output", None)
    if isinstance(llm_output, dict):
        if isinstance(llm_output.get("token_usage"), dict):
            return llm_output["token_usage"]
        if isinstance(llm_output.get("usage"), dict):
            return llm_output["usage"]

    try:
        gen0 = response.generations[0][0]
        meta = getattr(gen0, "response_metadata", None) or getattr(gen0, "generation_info", None)
        if isinstance(meta, dict):
            if isinstance(meta.get("token_usage"), dict):
                return meta["token_usage"]
            if isinstance(meta.get("usage"), dict):
                return meta["usage"]
    except Exception:
        pass

    return {}


class TokenUsageCallback(BaseCallbackHandler):
    def __init__(self, model_name: str, agent_name: str):
        self.model_name = model_name
        self.agent_name = agent_name

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs) -> None:
        usage = _extract_usage_dict(response)

        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens))

        cached_prompt_tokens = 0
        details = usage.get("prompt_tokens_details") or {}
        if isinstance(details, dict):
            cached_prompt_tokens = int(details.get("cached_tokens", 0))

        phase = get_current_phase()  

        global_usage_tracker.add(
            model=self.model_name,
            agent=self.agent_name,
            phase=phase,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_prompt_tokens=cached_prompt_tokens,
            meta={"raw": usage},
        )
