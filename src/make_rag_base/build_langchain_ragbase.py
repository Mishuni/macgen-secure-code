import os
import re
import json
import markdown
import requests
import pandas as pd
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


### FOR MARKDOWN CLEANING
def clean_markdown_full(md_text):
    md_text = re.sub(r'\[([^\]]*?)\]\([^)]+\)', r'\1', md_text)
    md_text = re.sub(r'(None known\s*)', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'(Related Guidelines|Bibliography)\s*[\s\S]*?(\n{2,}|$)', '', md_text, flags=re.IGNORECASE)
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


### FOR PDF CLEANING
section_keywords = ["Risk Assessment", "Related Guidelines", "Bibliography"]
REMOVE_PAGE_LABELS = [17, 27, 37, 43, 62, 67, 75, 91, 99, 108, 115, 123, 124, 134, 137, 143, 153, 166, 180, 184, 199, 207, 219, 228, 239, 250, 254, 258, 262, 276, 278, 281, 303, 313, 317, 324, 330, 339, 344, 348, 358, 363, 380, 395, 412, 432, 436, 447, 450]

FOOTER_PAT = re.compile(
    r"""
    ^SEI\ CERT\ C\ Coding\ Standard:\ Rules\ for\ Developing\ Safe,\ Reliable,\ and\ Secure\ Systems
    \s+\d+\s*
    \n
    Software\ Engineering\ Institute\ \|\ Carnegie\ Mellon\ University\s*
    \n
    \[DISTRIBUTION\ STATEMENT\ A] \ Approved\ for\ public\ release\ and\ unlimited\ distribution\.
    \s*$
    """,
    re.MULTILINE | re.VERBOSE,
)

FOOTER_PAT_CPP = re.compile(
    r"""
    SEI\ CERT\ C\+\+\ CODING\ STANDARD\ \(2016\ EDITION\)\s*\|\s*V\d+\s+\d+\s*
    Software\ Engineering\ Institute\s*\|\s*Carnegie\ Mellon\ University\s*
    \[DISTRIBUTION\ STATEMENT\ A\]\s*Approved\ for\ public\ release\ and\ unlimited\ distribution\.?\s*
    """,
    re.IGNORECASE | re.VERBOSE,
)


def remove_section_blocks(text: str, keywords) -> str:
    for keyword in keywords:
        pattern = rf"\n\d+\.\d+\.\d+\s+{re.escape(keyword)}.*?(?=\n\d+\.\d+\.\d+|\Z)"
        text = re.sub(pattern, "", text, flags=re.DOTALL)
    return text.strip()


class CleanFooterPDFLoader(PyPDFLoader):
    def __init__(self, file_path: str, cpp=False):
        super().__init__(file_path)
        self.footer_re = FOOTER_PAT_CPP if cpp else FOOTER_PAT

    def load(self, remove_page) -> list[Document]:
        docs = super().load()
        filtered_docs = []
        for d in docs:
            d.page_content = re.sub(self.footer_re, "", d.page_content).rstrip()
            page = int(d.metadata.get("page_label", "0"))
            if page not in remove_page:
                cleaned = remove_section_blocks(d.page_content, section_keywords)
                cleaned_lines = cleaned.strip().splitlines()
                if len(cleaned_lines) > 1:
                    filtered_docs.append(Document(page_content="\n".join(cleaned_lines), metadata=d.metadata))
        return filtered_docs


def load_CERT_C_documents(file_path: str, save_path: str = None, cpp=False):
    loader = CleanFooterPDFLoader(file_path, cpp=cpp)
    docs_ori = loader.load(REMOVE_PAGE_LABELS if not cpp else [])

    splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=600)
    docs_ori = splitter.split_documents(docs_ori)
    print(f"Split PDF into {len(docs_ori)} sub-documents.")

    split_docs = [doc for doc in docs_ori if len(doc.page_content) > 100]

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)
        print(f"Saved {len(split_docs)} documents to {save_path}.")

    return split_docs


def remove_spaced_words(text: str) -> str:
    return re.sub(r'(?:\b[A-Za-z]\b\s+){2,}[A-Za-z]\b', '', text)


def load_go_sec_guides(goscp_path: str, godev_url: str, save_path: str = None):
    pdf_loader = PyPDFLoader(goscp_path)
    pdf_docs = pdf_loader.load()
    for doc in pdf_docs:
        doc.page_content = remove_spaced_words(doc.page_content)

    response = requests.get(godev_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('article') or soup.find('body')
    text_content = main_content.get_text(separator='\n', strip=True)
    url_doc = Document(page_content=text_content, metadata={"source": godev_url})

    documents = pdf_docs + [url_doc]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(documents)
    split_docs = [doc for doc in split_docs if len(doc.page_content.strip()) >= 40]
    split_docs = split_docs[1:]

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(split_docs)} documents from Go sources.")
    return split_docs


def load_python_sec_guides(file_path: str = "../../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python", save_path: str = None):
    loader = DirectoryLoader(file_path, glob="**/*.md", loader_cls=TextLoader, show_progress=True)
    documents = loader.load()
    for doc in documents:
        doc.page_content = clean_markdown_full(doc.page_content)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(documents)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(split_docs)} documents from {file_path}.")
    return split_docs


def load_owasp_cheat_sheets(file_path: str = "../../CheatSheetSeries/cheatsheets", save_path: str = None):
    loader = DirectoryLoader(file_path, glob="**/*.md", loader_cls=TextLoader, show_progress=True)
    documents = loader.load()
    for doc in documents:
        doc.page_content = clean_markdown_full(doc.page_content)

    split_docs = [doc for doc in documents if len(doc.page_content) > 200]

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(split_docs)} documents from {file_path}.")
    return split_docs


def load_ASVS_documents(file_path: str):
    documents = []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data.get("requirements", []):
            content = item.get("req_description", "")
            content = re.sub(r"\(\[C\d+\]\(https://owasp\.org/www-project-proactive-controls/#div-numbering\)\)", "", content)
            metadata = {k: v for k, v in item.items() if k != "req_description"}
            documents.append(Document(page_content=content, metadata=metadata))

    print(f"Loaded {len(documents)} documents from {file_path}.")
    return documents


def load_vectorstore_from_path(path: str):
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)
    return vectorstore


def run_test_query(db_path: str, query: str):
    print(f"\n--- Testing RAG DB: {db_path} ---")
    print(f"Query: {query}")
    vectorstore = load_vectorstore_from_path(db_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    results = retriever.invoke(query)
    for i, doc in enumerate(results):
        print(f"\n--- Document {i+1} (source: {doc.metadata.get('source', 'N/A')}, page: {doc.metadata.get('page', 'N/A')}) ---")
        print(doc.page_content)
    print(f"--- End of test for {db_path} ---\n")


def row_to_text(row):
    parts = [
        f"CWE-ID: {row['CWE-ID']}",
        f"Name: {row['Name']}",
        f"Description: {row.get('Description', '')}",
        f"Mitigations: {row.get('Potential Mitigations', '')}",
    ]
    return "\n".join(str(p) for p in parts if p)


def load_cwe_document(csv_path='../../data/rc_cwe_list.csv'):
    df_cwe_list = pd.read_csv(csv_path, index_col=False, header=0)
    selected_columns = ['CWE-ID', 'Name', 'Related Weaknesses', 'Status', 'Description', 'Potential Mitigations']
    df_cwe_selected = df_cwe_list[selected_columns].copy()
    df_cwe_selected = df_cwe_selected[df_cwe_selected['Status'] == 'Stable']

    df_cwe_selected['Related Weaknesses'] = df_cwe_selected['Related Weaknesses'].apply(
        lambda text: [int(x) for x in re.findall(r"CWE ID:(\d+)", str(text))] if pd.notnull(text) else []
    )
    df = df_cwe_selected.copy()

    docs = [
        Document(
            page_content=row_to_text(r),
            metadata={
                "cwe_id": int(r["CWE-ID"]) if str(r["CWE-ID"]).isdigit() else str(r["CWE-ID"]),
                "name": r["Name"],
                "related": r.get("Related Weaknesses", []),
                "description": r.get("Description", ""),
            },
        )
        for _, r in df.iterrows()
    ]

    return docs


def format_docs(docs):
    out = []
    for d in docs:
        out.append(f"[CWE-{d.metadata.get('cwe_id')}] {d.metadata.get('name')}, ")
    return "\n---\n".join(out)


def load_documents_from_json(json_path: Path) -> List[Document]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for item in data:
        if isinstance(item, dict):
            text = item.get("text") or item.get("content")
            metadata = item.get("metadata", {})
        else:
            text = str(item)
            metadata = {}

        if text:
            documents.append(Document(page_content=text, metadata=metadata))

    return documents


def make_vectorstore_from_documents(documents, save_path=None):
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(documents, embedding)
    print(f"Vectorstore created with {len(documents)} documents.")

    if save_path:
        vectorstore.save_local(save_path)
        print(f"Saved FAISS index to: {save_path}")

    return vectorstore


def build_faiss_for_json(json_path: str):
    json_path = Path(json_path)
    save_dir = json_path.parent / "faiss_index"

    print(f"\n[+] Processing: {json_path}")
    docs = load_documents_from_json(json_path)
    make_vectorstore_from_documents(docs, save_path=str(save_dir))
