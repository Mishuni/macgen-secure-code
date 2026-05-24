
import re,json

def format_step(step: str) -> str:
    if step is None:
        return ''
    return step.strip('\n').strip()


def strip_think_tags(text: str) -> str:
    """Remove <think>...</think> sections from model output."""
    if not text:
        return ""
    # Primary behavior: remove hidden reasoning blocks.
    stripped = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    if stripped:
        return stripped
    # Fallback: some models wrap the *entire* answer in <think>...</think>.
    # In that case, avoid returning empty output; remove only the tags.
    return re.sub(r"</?think>", "", text, flags=re.IGNORECASE).strip()

def to_text(output) -> str:
    """
    Safely extract and return text content from LangChain Message or raw output as a string.
    - str: returned as-is
    - AIMessage/object: extract .content; if list, concatenate text parts
    """
    if isinstance(output, str):
        return output
    content = getattr(output, "content", output)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text" and "text" in part:
                    texts.append(str(part["text"]))
                elif "text" in part:
                    texts.append(str(part["text"]))
                else:
                    texts.append(str(part))
            else:
                texts.append(str(part))
        return "\n".join([t for t in texts if t]).strip()
    return str(content or "")


STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"')
def remove_codeblocks(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"<CODE>.*?</CODE>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text


# JSON sanitization utilities
def _fix_string_literal(match: re.Match) -> str:
    s = match.group(0)
    inner = s[1:-1]

    def esc(ch: str) -> str:
        o = ord(ch)
        if ch == "\n":
            return r"\n"
        if ch == "\r":
            return r"\r"
        if ch == "\t":
            return r"\t"
        if 0 <= o < 0x20:
            return "\\u%04x" % o
        return ch

    inner = "".join(esc(c) for c in inner)
    inner = re.sub(r"(?<!\\)\\(?![\"\\/bfnrtu])", r"\\", inner)
    return '"' + inner + '"'

def sanitize_json_text(bad_json_text: str) -> str:
    return STRING_RE.sub(_fix_string_literal, bad_json_text)


def safe_json_loads(text: str) :
    text = text.replace("cwe-", "CWE-").replace("CWE- ", "CWE-")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed = sanitize_json_text(text)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            # Some json libs accept strict=False; stock json also supports it
            return json.loads(fixed, strict=False)


