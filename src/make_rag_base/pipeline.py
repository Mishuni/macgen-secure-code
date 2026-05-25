import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from build_langchain_ragbase import (
    load_owasp_cheat_sheets,
    load_CERT_C_documents,
    load_js_sec_guides,
    load_go_sec_guides,
    load_python_sec_guides,
    build_faiss_for_json,
)

# ── Pipeline flags ────────────────────────────────────────────────────────────
REFINE_DOCUMENT = False   # True: run LLM refinement (step 2) before building FAISS
REFINE_MODEL    = "gpt-5.1"
DATA_ROOT       = Path("data/rag_databases")

# ── Source config ─────────────────────────────────────────────────────────────
# Each entry defines how to load, where to save raw/refined JSON, and the language for refinement.
# Comment/uncomment sources to control which ones run.
SOURCES = {
    "owasp": {
        "loader": lambda save_path: load_owasp_cheat_sheets(
            file_path="../../sec/CheatSheetSeries/cheatsheets",
            save_path=save_path,
        ),
        "raw_json":     DATA_ROOT / "OWASP_CheatSheets_faiss/owasp_cheatsheet_docs.json",
        "refined_json": DATA_ROOT / "OWASP_CheatSheets_faiss/owasp_cheatsheet_docs_refined.json",
        "language":     None,
    },
    # "cert_c": {
    #     "loader": lambda save_path: load_CERT_C_documents(
    #         file_path="data/SEI CERT C Coding Standard_rules.pdf",
    #         save_path=save_path,
    #     ),
    #     "raw_json":     DATA_ROOT / "CERT_C_faiss/CERT_C.json",
    #     "refined_json": DATA_ROOT / "CERT_C_faiss/CERT_C_refined.json",
    #     "language":     "C",
    # },
    # "cert_cpp": {
    #     "loader": lambda save_path: load_CERT_C_documents(
    #         file_path="data/SEI CERT CPP Coding Standard_rules.pdf",
    #         save_path=save_path,
    #         cpp=True,
    #     ),
    #     "raw_json":     DATA_ROOT / "CERT_CPP_faiss/CERT_CPP.json",
    #     "refined_json": DATA_ROOT / "CERT_CPP_faiss/CERT_CPP_refined.json",
    #     "language":     "C++",
    # },
    # "go": {
    #     "loader": lambda save_path: load_go_sec_guides(
    #         goscp_path="../Go-SCP/dist/go-webapp-scp.pdf",
    #         godev_url="https://go.dev/doc/security/",
    #         save_path=save_path,
    #     ),
    #     "raw_json":     DATA_ROOT / "Go_faiss/Go.json",
    #     "refined_json": DATA_ROOT / "Go_faiss/Go_refined.json",
    #     "language":     "Go",
    # },
    # "python": {
    #     "loader": lambda save_path: load_python_sec_guides(
    #         file_path="../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python",
    #         save_path=save_path,
    #     ),
    #     "raw_json":     DATA_ROOT / "Python_faiss/python.json",
    #     "refined_json": DATA_ROOT / "Python_faiss/python_refined.json",
    #     "language":     "Python",
    # },
}


def step1_load(name: str, cfg: dict):
    print(f"\n[Step 1] Loading raw documents: {name}")
    cfg["loader"](save_path=str(cfg["raw_json"]))


def step2_refine(name: str, cfg: dict):
    print(f"\n[Step 2] Refining with LLM: {name}")
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "refine_raw_document.py"),
        "--input",  str(cfg["raw_json"]),
        "--output", str(cfg["refined_json"]),
        "--model",  REFINE_MODEL,
    ]
    if cfg.get("language"):
        cmd += ["--language", cfg["language"]]
    subprocess.run(cmd, check=True)


def step3_faiss(name: str, cfg: dict):
    print(f"\n[Step 3] Building FAISS index: {name}")
    json_path = cfg["refined_json"] if REFINE_DOCUMENT else cfg["raw_json"]
    build_faiss_for_json(str(json_path))


if __name__ == "__main__":
    for name, cfg in SOURCES.items():
        step1_load(name, cfg)
        if REFINE_DOCUMENT:
            step2_refine(name, cfg)
        step3_faiss(name, cfg)
