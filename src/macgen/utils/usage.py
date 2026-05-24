# macgen/utils/usage.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List
import json

@dataclass
class UsageRecord:
    model: str
    agent: str
    phase: str      
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_prompt_tokens: int = 0
    meta: Dict[str, Any] | None = None


class UsageTracker:
    def __init__(self) -> None:
        self.records: List[UsageRecord] = []

    def add(
        self,
        model: str,
        agent: str,
        phase: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cached_prompt_tokens: int = 0,
        meta: Dict[str, Any] | None = None,
    ) -> None:
        self.records.append(
            UsageRecord(
                model=model,
                agent=agent,
                phase=phase,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cached_prompt_tokens=cached_prompt_tokens,
                meta=meta or {},
            )
        )

    def to_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.records], f, indent=2, ensure_ascii=False)

    def summary(self) -> Dict[str, Dict[str, int]]:
        agg: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r in self.records:
            key = f"{r.agent}:{r.phase}"
            agg[key]["prompt_tokens"] += r.prompt_tokens
            agg[key]["completion_tokens"] += r.completion_tokens
            agg[key]["total_tokens"] += r.total_tokens
            agg[key]["cached_prompt_tokens"] += r.cached_prompt_tokens
        return agg


global_usage_tracker = UsageTracker()
_current_phase: str = "unknown"

def set_current_phase(phase: str) -> None:
    global _current_phase
    _current_phase = phase

def get_current_phase() -> str:
    return _current_phase





PRICES = {
    "gpt4o": {
        "prompt": 2.5 / 1_000_000,      # $2.50 / 1M
        "completion": 10.00 / 1_000_000,  # $10.00 / 1M
        "cache_prompt_discount": 0.5,   # 50% discount 
    },
    "gpt4o-mini": {
        "prompt": 0.15 / 1_000_000,      # $0.15 / 1M
        "completion": 0.6 / 1_000_000,  # $0.10 / 1M
        "cache_prompt_discount": 0.5,   # 50% discount 
    },
}

def compute_cost(usage_json: Path):
    with usage_json.open("r", encoding="utf-8") as f:
        records = json.load(f)

    total_cost = 0.0
    for r in records:
        model = r["model"]
        price = PRICES.get(model)
        if not price:
            continue

        pt = r["prompt_tokens"]
        ct = r["completion_tokens"]
        cached = r.get("cached_prompt_tokens", 0)
        uncached = max(pt - cached, 0)

        effective_prompt_tokens = (
            uncached + cached * price.get("cache_prompt_discount", 1.0)
        )

        cost = (
            effective_prompt_tokens * price["prompt"]
            + ct * price["completion"]
        )
        total_cost += cost

    print(f"Total cost (approx): ${total_cost:.10f}")
    return total_cost
