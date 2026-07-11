# make_rag_base

Builds the FAISS vector stores used as the security knowledge base in MACGen.

## Pipeline Overview

The build process runs in three steps, orchestrated by `pipeline.py`:

```
Step 1 (load)    Raw documents (PDF / Markdown / JSON)
                      ↓  load_* functions in build_langchain_ragbase.py
                 raw JSON  (data/refined_raw_documents_v4/.../xxx.json)

Step 2 (refine)  raw JSON
                      ↓  refine_raw_document.py  [optional, REFINE_DOCUMENT=True]
                 refined JSON  (.../xxx_refined.json)

Step 3 (faiss)   raw or refined JSON
                      ↓  build_faiss_for_json
                 FAISS index  (.../faiss_index/)
```

Set `REFINE_DOCUMENT = False` in `pipeline.py` to skip Step 2 and build FAISS directly from the raw JSON.

## Running

```bash
cd MACGen
python src/make_rag_base/pipeline.py
```

To enable/disable specific sources, comment/uncomment entries in the `SOURCES` dict in `pipeline.py`.

To run only the LLM refinement step manually:

```bash
python src/make_rag_base/refine_raw_document.py \
  --input  data/rag_database/OWASP_CheatSheets_faiss/owasp_cheatsheet_docs.json \
  --output data/rag_database/OWASP_CheatSheets_faiss/owasp_cheatsheet_docs_refined.json \
  --language None
```

## Security Knowledge Sources

The knowledge base is constructed from authoritative and widely adopted standards, covering general application security as well as language-specific secure coding practices.

| Scope | Source | File(s) | Snapshot pinned in this release |
|---|---|---|---|
| **General** | [OWASP Application Security Verification Standard (ASVS) 5.0.0](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json) | `OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json` | git tag `v5.0.0` (immutable release) |
| **General** | [OWASP Cheat Sheet Series](https://github.com/OWASP/CheatSheetSeries/tree/9f9424ae0237ae3f21ab24e8ea98c9ef243bb01d/cheatsheets) | `../CheatSheetSeries/cheatsheets/` | commit `9f9424ae0237ae3f21ab24e8ea98c9ef243bb01d` (2025-08-01) |
| **C** | [SEI CERT C Coding Standard (2016 Edition)](https://wiki.sei.cmu.edu/confluence/display/c) | `SEI_CERT_C_Coding_Standard_2016_Edition.pdf` | 2016 Edition PDF, document revision 2016-08-02 (per PDF metadata) |
| **C++** | [SEI CERT C++ Coding Standard (2016 Edition)](https://wiki.sei.cmu.edu/confluence/display/cplusplus) | `SEI CERT CPP Coding Standard.pdf` | 2016 Edition PDF, document revision 2017-03-09 (per PDF metadata) |
| **Python** | [OpenSSF Secure Coding Guide for Python](https://github.com/ossf/wg-best-practices-os-developers/tree/2d583f58a216a0f197277e41aabced975b8a9950/docs/Secure-Coding-Guide-for-Python) | `../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python/` | commit `2d583f58a216a0f197277e41aabced975b8a9950` (2025-07-29) |
| **Go** | [OWASP Go Web Application Secure Coding Practices](https://github.com/OWASP/Go-SCP/tree/e6c92359bb1733c14c9d1a5218144c8102f82df0) | `../Go-SCP/dist/go-webapp-scp.pdf` | commit `e6c92359bb1733c14c9d1a5218144c8102f82df0` / tag `v2.6.6` (2024-05-31) |
| **JavaScript** | [nodebestpractices — security section](https://github.com/goldbergyoni/nodebestpractices/tree/c0b71ccf3a134443635da6886423b44e31e65a73/sections/security) | `../nodebestpractices/sections/security/` | commit `c0b71ccf3a134443635da6886423b44e31e65a73` (2025-04-16) |

For languages without a dedicated source in the corpus, the general sources (ASVS, OWASP Cheat Sheets) are used. JavaScript additionally merges the OWASP Cheat Sheets index at retrieval time (`src/macgen/rag.py`, `_REL_PATHS["javascript"]`); Rust/PHP/Ruby fall back to ASVS only.

### Reproducibility: exact snapshot dates

Each GitHub-hosted source above was cloned once and never re-pulled (verified via `git reflog`), so the commit pinned in the table is exactly what was on disk when the FAISS indices actually used at generation time (`refined_raw_documents_v3/` in the working repo) were built:

- `CERT_C_faiss/`, `CERT_CPP_faiss/`, `Go_faiss/`, `Python_faiss/`, `JavaScript_faiss/` were built **2026-04-13/14**; `ASVS_faiss/` was built **2026-04-08** and is shared unchanged across all pipeline variants.
- `OWASP_CheatSheets_faiss/` was rebuilt **2026-05-26** (OWASP source only; same pinned commit, re-run for a pipeline change unrelated to source content).
- `CERT_C_faiss/`, `CERT_CPP_faiss/`, `Go_faiss/`, `Python_faiss/`, and `OWASP_CheatSheets_faiss/` in `data/rag_databases/` here were repackaged **2026-05-24/26** for release; content is byte-identical to the originals above (verified via `diff`). `JavaScript_faiss/` was copied in directly from the original 2026-04-13 build (it had been omitted from the initial release packaging).

The CERT C/C++ PDFs are not redistributable in this repo, but the extracted and LLM-refined text we actually embed is committed directly at `data/rag_databases/CERT_C_faiss/CERT_C_refined.json` and `data/rag_databases/CERT_CPP_faiss/CERT_CPP_refined.json` — so exact reproduction of the knowledge base does not require re-acquiring the PDFs.

## File Structure

```
make_rag_base/
├── pipeline.py                  # Orchestrator: runs step 1 → (2) → 3
├── build_langchain_ragbase.py   # Document loaders + FAISS builder
├── refine_raw_document.py       # LLM-based guideline refinement (CLI)
└── build_cwe_coverage.py        # Utility: CWE coverage analysis
```
