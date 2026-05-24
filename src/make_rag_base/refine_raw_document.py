#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI  # pip install openai

CWE_HEADER_RE = re.compile(r"(CWE-\d+)\s*:\s*([^\n\r]+)")

# ---- Your "line -> guideline text" prompt (English, plain text) ----
LINE_PROMPT = """Extract security-guideline information for {LANGUAGE} from the following paragraph.

Rewrite it as a reusable security guideline in plain text.
Return ONLY the guideline text. Do NOT use JSON. Do NOT add any extra commentary.
If no security content is found, return an empty string.

Output format:
1) First line MUST be one of:
   - "CWE-XXXX: <CWE name>" if a CWE ID is explicitly present, OR
   - "<short title>" if no CWE ID is found.
2) Then include the sections below. Each section can be 1–2 lines.
   WHAT:  What is the security issue? Include the concrete failure mode.
   WHY:   Why it matters (impact).
   HOW:   How to fix. Provide actionable steps/checks, not vague advice.
   EXAMPLE: Provide a minimal before/after code snippet OR a concrete code pattern if possible (if language is not specified, do not provide an example).

Detail requirements:
- Prefer specific triggers/conditions (e.g., “if path is user-controlled”, “if identifier shadows builtins”).
- Prefer concrete mitigation (e.g., “use X API flag”, “validate with allowlist”, “normalize then check prefix”)
- Keep total output ≤ 6 lines.

Filtering rules:
- Do NOT infer missing CWE IDs or facts.

Input paragraph:
{LINE}

Output:
"""

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def iter_documents(obj: Any) -> Iterable[Tuple[str, Dict[str, Any]]]:
    """
    Tries to iterate documents from various common JSON shapes.
    Yields (doc_id, doc_dict).
    """
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                yield (str(item.get("id", i)), item)
            else:
                yield (str(i), {"text": str(item)})
        return

    if isinstance(obj, dict):
        # common keys
        for key in ("documents", "docs", "items", "data"):
            if key in obj and isinstance(obj[key], list):
                for i, item in enumerate(obj[key]):
                    if isinstance(item, dict):
                        yield (str(item.get("id", i)), item)
                    else:
                        yield (str(i), {"text": str(item)})
                return

        # fallback: treat whole dict as one document
        yield ("0", obj)
        return

    # unknown shape: one doc
    yield ("0", {"text": str(obj)})

def extract_text(doc: Dict[str, Any]) -> str:
    """
    Pulls text from likely fields. Adjust these keys if your CERT_C.json uses a specific schema.
    """
    for k in ("text", "content", "page_content", "document", "raw", "chunk", "body"):
        v = doc.get(k)
        if isinstance(v, str) and v.strip():
            return v
    # sometimes nested
    if isinstance(doc.get("metadata"), dict):
        for k in ("text", "content"):
            v = doc["metadata"].get(k)
            if isinstance(v, str) and v.strip():
                return v
    # last resort: stringify
    return json.dumps(doc, ensure_ascii=False)

# def extract_cwe_header(full_text: str) -> Optional[str]:
#     m = CWE_HEADER_RE.search(full_text)
#     if not m:
#         return None
#     cwe_id = m.group(1).strip()
#     name = m.group(2).strip()
#     # normalize
#     name = re.sub(r"\s+", " ", name)
#     return f"{cwe_id}: {name}"

def normalize_lines(text: str) -> List[str]:
    # Keep code lines too; your prompt will decide whether to output EXAMPLE or nothing.
    lines = [ln.strip("\ufeff") for ln in text.splitlines()]
    # Drop empty-only quickly (still okay if you want to keep them; prompt would output nothing)
    return [ln.rstrip() for ln in lines]

def call_model_line(client: OpenAI, model: str, line: str, temperature: float = 0.0, language = None, max_tokens = 1200) -> str:
    prompt = LINE_PROMPT.format(LINE=line,LANGUAGE=language if language else "programming")
    print(f"DEBUG: prompt=\n{prompt}\n---")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        # max_tokens=max_tokens,
    )
    print(f"DEBUG: resp=\n{resp.choices[0].message.content.strip()}\n---")

    return resp.choices[0].message.content.strip()
def build_guideline_block(
    client: OpenAI,
    model: str,
    doc_id: str,
    text: str,
    sleep_s: float = 0.0,
    temperature: float = 0.0,
    max_lines: Optional[int] = None,
) -> str:
    # header = extract_cwe_header(text) or "CWE-UNKNOWN: Unknown"

    out_lines: List[str] = []
    # seen = set([header])
    seen = set()

    # lines = normalize_lines(text)
    # if max_lines is not None:
    #     lines = lines[:max_lines]

    # for ln in lines:
    if True:
        ln = text
        if not ln.strip():
            return

        extracted = call_model_line(client, model=model, line=ln, temperature=temperature)
        if not extracted:
            return

        # The model might return multiple lines (WHAT/HOW/EXAMPLE). Keep them if new.
        for el in extracted.splitlines():
            el = el.strip()
            if not el:
                continue
            # seen.add(el)
            out_lines.append(el)
            # Avoid accidentally repeating the header elsewhere; we already force it to the top.
            # if el.startswith("CWE-"):
            #     continue
            # if el not in seen:
            #     out_lines.append(el)
            #     seen.add(el)

        # if sleep_s > 0:
        #     time.sleep(sleep_s)

    return "\n".join(out_lines).rstrip() + "\n"

def deduplicate(docs: List[str], threshold: float = 0.75) -> List[str]:
    docs = [d for d in docs if d and d.strip()]
    if len(docs) == 0:
        return docs

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs)
    sim_matrix = cosine_similarity(tfidf)

    keep = set(range(len(docs)))
    for i in range(len(docs)):
        if i not in keep:
            continue
        for j in range(i + 1, len(docs)):
            if j in keep and sim_matrix[i][j] > threshold:
                keep.remove(j)

    result = [docs[i] for i in sorted(keep)]
    print(f"Dedup: {len(docs)} → {len(result)} (threshold={threshold})")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to input JSON (raw docs or already-refined JSON array)")
    ap.add_argument(
        "--output",
        required=True,
        help="Output .json file to write extracted security guidelines (JSON array)"
    )
    ap.add_argument("--language", default=None, help="Programming language of the guidelines")
    ap.add_argument("--model", default="gpt-5.1", help="Model name (e.g., gpt-5.1)")
    ap.add_argument("--sleep", type=float, default=0.4, help="Seconds to sleep between API calls (rate-limit friendly)")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max_docs", type=int, default=None)
    ap.add_argument("--max_lines", type=int, default=None, help="Optional cap per doc for quick tests")
    ap.add_argument("--dedup_only", action="store_true",
                    help="Skip LLM calls. Load --input as a refined JSON array, deduplicate, and save to --output.")
    ap.add_argument("--dedup_threshold", type=float, default=0.75,
                    help="Cosine similarity threshold for deduplication (default: 0.75)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # ── dedup-only mode ──────────────────────────────────────────────────────
    if args.dedup_only:
        blocks: List[str] = load_json(args.input)
        if not isinstance(blocks, list):
            raise ValueError("--dedup_only expects a JSON array as input.")
        blocks = deduplicate(blocks, threshold=args.dedup_threshold)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(blocks, f, ensure_ascii=False, indent=2)
        print(f"Done. Wrote: {args.output}")
        return

    # ── normal LLM mode ──────────────────────────────────────────────────────
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Export it first: export OPENAI_API_KEY='...'" )

    client = OpenAI()

    obj = load_json(args.input)

    blocks: List[str] = []
    for idx, (doc_id, doc) in enumerate(iter_documents(obj)):
        if args.max_docs is not None and idx >= args.max_docs:
            break
        text = extract_text(doc)
        if text is None: continue
        block = build_guideline_block(
            client=client,
            model=args.model,
            doc_id=doc_id,
            text=text,
            sleep_s=args.sleep,
            temperature=args.temperature,
            max_lines=args.max_lines,
        )
        # add a separator between docs
        blocks.append(block)
        # blocks.append("\n" + ("-" * 60) + "\n")
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(blocks, f, ensure_ascii=False, indent=2)

        # lightweight progress
        print(f"[{idx+1}] processed doc_id={doc_id}, chars={len(text)}")
        # break

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)

    print(f"Done. Wrote: {args.output}")

if __name__ == "__main__":
    main()

#     python refine_raw_document.py \
#   --dedup_only \
#   --input  data/refined_raw_documents/CERT_C_faiss/CERT_C_refined.json \
#   --output data/refined_raw_documents/CERT_C_faiss/CERT_C_deduped.json \
#   --dedup_threshold 0.75
