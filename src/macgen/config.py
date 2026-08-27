from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import yaml
from pathlib import Path
from enum import Enum


@dataclass
class EngineConfig:
    task: str = "llmseceval"  # "cweval" "llmseceval" "humaneval"
    model_name: str = (
        "gpt4o-mini"  # "gpt4o-mini" "gpt4o" "gemini-2.5-flash-lite" "gemini-2.5-flash" "deepseek-r1_70b"
    )
    os_platform: str = "linux"
    temperature: float = 0.0
    max_tokens: int = 1500
    max_cwe_limit: int = 3
    with_plan: bool = True
    # max_plan_steps: int = 1
    cwe_extract: bool = True
    with_rag: bool = True
    with_sec_guide: bool = True
    make_draft_code: bool = True

    with_sec_else_draft: bool = True
    with_analyze_draft_surface: bool = True
    with_sec_all_history: bool = False
    with_sec_guide_validate: bool = True
    with_pre_understand: bool = False

    already_cwe: bool = False
    already_plan: bool = False
    already_code: bool = False
    already_sec_guide: bool = False
    already_rag: bool = False
    already_draft_code: bool = False
    only_plan: bool = False
    only_direct: bool = False
    only_rag: bool = False
    save_res: bool = True  # True
    sec_docs_rag_k: int = 2  # 3 # 3 #5 #3
    load_preset: bool = True
    preset_file: Optional[str] = None
    rescue_guide_file: Optional[str] = None  # path to eval results JSON for precomputed sec_guidelines snippets

    ## ===== Phase 2
    enable_phase2: bool = False
    max_refinement_attempts: int = 2
    enable_functionality_check: bool = True
    enable_security_check: bool = True

    @classmethod
    def from_yaml(cls, path: str) -> "EngineConfig":
        cfg_dict = cls._load_yaml_with_base(path)
        return cls(**cfg_dict)

    @staticmethod
    def _load_yaml_with_base(path: str) -> dict:
        """Load a YAML config, recursively merging any `_base_` reference."""
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            cfg_dict = yaml.safe_load(f) or {}
        base_ref = cfg_dict.pop("_base_", None)
        if base_ref:
            base_path = (p.parent / base_ref).resolve()
            base_dict = EngineConfig._load_yaml_with_base(str(base_path))
            base_dict.update(cfg_dict)
            return base_dict
        return cfg_dict


# =============================
# Core engine
# =============================
def config_to_str(cfg: EngineConfig) -> str:
    lines = []
    for field, value in vars(cfg).items():
        lines.append(f"{field}={value}")
    return "\n".join(lines)


# =============================
# Data access
# =============================
CSV_PATH = Path("./data/rc_cwe_list.csv")
CWE_TREE_PATH = Path("./data/cwe_tree.jsonl")
EXCLUDE_LSE = [
    53,
    58,
    59,
    60,
    61,
    62,
    80,
    81,
    82,
    84,
    85,
    86,
    88,
    90,
    91,
    92,
    93,
    96,
    98,
    139,
]


model_mapping = {
    "gpt-o4-mini": "o4-mini-2025-04-16",
    "gpt4-nano": "gpt-4.1-nano-2025-04-14",
    "gpt4o-mini": "gpt-4o-mini-2024-07-18",
    "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
    "gpt3.5": "gpt-3.5-turbo",
    "gpt4": "gpt-4.1",
    "gpt4-mini": "gpt-4.1-mini",
    "gpt4o": "gpt-4o",
    "gpt5": "gpt-5",
    "gpt5-mini": "gpt-5-mini",
    "gpt5-nano": "gpt-5-nano",
    "gpt5.1": "gpt-5.1",
    "gpt-5.1": "gpt-5.1",
    
    # Google Gemini
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    
    # Ollama
    "deepseek-r1_70b": "deepseek-r1:70b",
    "qwen3_4b": "qwen3:4b",
    "qwen3_8b": "qwen3:8b",
    "qwen3_14b": "qwen3:14b",
    "qwen3_32b": "qwen3:32b",
    "qwen3-coder_30b": "qwen3-coder:30b",
    "llama3.1_8b": "llama3.1:8b",

    # Anthropic Claude
    "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
    "claude-3.5-haiku": "claude-3-5-haiku-20241022",
    "claude-4-sonnet": "claude-sonnet-4-20250514",
    "claude-4-opus": "claude-opus-4-20250514",
    "claude-opus-4-6": "claude-opus-4-6",
}

SAFE_CODER_FILES_DIRECTORY = "./data/safe_coder_eval"

LANGUAGE_SUFFIX_MAPS = {
    "py": "python",
    "c": "c",
    "cpp": "c++",
    "h": "c++",
    "cc": "c++",
    "hpp": "c++",
    "cs": "csharp",
    "cs": "c#",
    "js": "javascript",
    "jsx": "javascript",
    "rb": "ruby",
    "go": "go",
    "java": "java",
    "php": "php",
}


class AgentStrategy(Enum):
    INDICT_LLAMA = "indict_llama"
    INDICT_COMMANDR = "indict_commandr"


strategy_mapping = {}
for s in AgentStrategy:
    strategy_mapping[s.value] = s.name

QL_LANGUAGES = ["python", "cpp", "javascript", "java", "go", "ruby"]  # , 'typescript']
CODEQL_ROOT_DIR = "./codeql/codeql-repo/"

LANGUAGE_MAPS = {
    "python": "python",
    "py": "python",
    "c": "cpp",
    "cpp": "cpp",
    "c++": "cpp",
    "c#": "csharp",
    "csharp": "csharp",
    "javascript": "javascript",
    "jsx": "javascript",
    "typescript": "javascript",
    "ruby": "ruby",
    "go": "go",
    "java": "java",
}
