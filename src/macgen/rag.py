from typing import Any, Dict, Optional, Tuple
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
# from pathlib import Path

def load_vectorstore_from_path(path: str):
    embedding =  OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)
    return vectorstore

class RAGManager:
    """Manages language-specific RAG indices with optional multi-base merge.
    - Caches retrievers per (language, k)
    - Supports path lists (will merge stores)
    """
    DEFAULT_PATHS = {
        "c": ["data/rag_databases/CERT_C_faiss/faiss_index" , "data/rag_databases/ASVS_faiss"],  
        "c++": ["data/rag_databases/CERT_CPP_faiss/faiss_index"], 
        "cpp": ["data/rag_databases/CERT_CPP_faiss/faiss_index"], 
        "python": ["data/rag_databases/Python_faiss/faiss_index", "data/rag_databases/ASVS_faiss"],  
        "py": ["data/rag_databases/Python_faiss/faiss_index", "data/rag_databases/ASVS_faiss"],  
         "javascript": [ "data/refined_raw_documents_v3/JavaScript_faiss/faiss_index","data/refined_raw_documents_v3/OWASP_CheatSheets_faiss/faiss_index","data/refined_raw_documents/ASVS_faiss"],
        "go": [ "data/rag_databases/Go_faiss/faiss_index", "data/rag_databases/ASVS_faiss"],  
        "rust": [ "data/rag_databases/ASVS_faiss"],
        "php": [ "data/rag_databases/ASVS_faiss"],
        "ruby": [ "data/rag_databases/ASVS_faiss"],
    }

    def __init__(self, k: int = 3):
        self.k_default = k
        self._cache: Dict[Tuple[str, int], Any] = {}

    def _build_vectorstore(self, paths: list[str]):
        vs = load_vectorstore_from_path(paths[0])
        for p in paths[1:]:
            vs2 = load_vectorstore_from_path(p)
            # Merge docstores (FAISS wrapper assumed)
            vs.add_documents(vs2.docstore._dict.values())
        return vs

    def get_retriever(self, language: str, k: Optional[int] = None):
        k = k or self.k_default
        key = (language.lower(), None)
        if key is None:
            raise NotImplementedError("Language-specific retriever not implemented")
        if key in self._cache:
            return self._cache[key]
        paths = self.DEFAULT_PATHS.get(language.lower(), [])
        vs = self._build_vectorstore(paths)
        ret = vs.as_retriever(search_kwargs={"k": k})
        self._cache[key] = ret
        return ret
