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

| Scope | Source | File(s) |
|---|---|---|
| **General** | [OWASP Application Security Verification Standard (ASVS) 5.0.0](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json) | `OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json` |
| **General** | [OWASP Cheat Sheet Series](https://github.com/OWASP/CheatSheetSeries/tree/master/cheatsheets) | `../CheatSheetSeries/cheatsheets/` |
| **C / C++** | [SEI CERT C Coding Standard (2016 Edition)](https://wiki.sei.cmu.edu/confluence/display/c) | `SEI CERT C Coding Standard_rules.pdf` |
| **C / C++** | [SEI CERT C++ Coding Standard (2016 Edition)](https://wiki.sei.cmu.edu/confluence/display/cplusplus) | `SEI CERT CPP Coding Standard.pdf` |
| **Python** | [OpenSSF Secure Coding Guide for Python](https://github.com/ossf/wg-best-practices-os-developers) | `../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python/` |
| **Go** | [OWASP Go Web Application Secure Coding Practices](https://github.com/OWASP/Go-SCP) | `../Go-SCP/dist/go-webapp-scp.pdf` |

For languages without a dedicated source in the corpus, the general sources (ASVS, OWASP Cheat Sheets) are used.

## File Structure

```
make_rag_base/
├── pipeline.py                  # Orchestrator: runs step 1 → (2) → 3
├── build_langchain_ragbase.py   # Document loaders + FAISS builder
├── refine_raw_document.py       # LLM-based guideline refinement (CLI)
└── build_cwe_coverage.py        # Utility: CWE coverage analysis
```
