import os
import markdown, re
import requests
from dotenv import load_dotenv

load_dotenv()
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import pandas as pd
import re
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from langchain_core.documents import Document

### FOR MARKDOWN CLEANING
def clean_markdown_full(md_text):
    # 1. remove hyper link: [text](url) → text
    md_text = re.sub(r'\[([^\]]*?)\]\([^)]+\)', r'\1', md_text)
    # 2. remove table:
    # md_text = re.sub(r'^\|.*\|\s*$', '', md_text, flags=re.MULTILINE)
    # 3. remove appendix sections (None known, Related Guidelines, Bibliography)
    md_text = re.sub(r'(None known\s*)', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'(Related Guidelines|Bibliography)\s*[\s\S]*?(\n{2,}|$)', '', md_text, flags=re.IGNORECASE)
    # 4. HTML parsing and cleaning up markdown
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

### FOR PDF CLEANING
section_keywords = [
    "Risk Assessment",
    "Related Guidelines",
    "Bibliography"
]
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
        # ex) 10.1.6 Risk Assessment ... 
        pattern = rf"\n\d+\.\d+\.\d+\s+{re.escape(keyword)}.*?(?=\n\d+\.\d+\.\d+|\Z)"
        text = re.sub(pattern, "", text, flags=re.DOTALL)
    return text.strip()


class CleanFooterPDFLoader(PyPDFLoader):
    def __init__(self, file_path: str, cpp=False):
        super().__init__(file_path)
        self.cpp = cpp
        if cpp:
            self.footer_re = FOOTER_PAT_CPP
        else:
            self.footer_re = FOOTER_PAT
            
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

def load_CERT_C_documents(file_path: str, cpp=False):
    loader = CleanFooterPDFLoader(file_path, cpp=cpp)
    # if not cpp :
    #     docs_ori = loader.load(REMOVE_PAGE_LABELS)
    # else:
    docs_ori = loader.load([])
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=600
    )
    docs_ori = splitter.split_documents(docs_ori)
    
    print(f"Split PDF into {len(docs_ori)} sub-documents.")
    
    after_docs = []
    split_docs = [doc for doc in docs_ori if len(doc.page_content) > 100]  # Filter out too short documents
    for i, doc in enumerate(split_docs):
        after_docs.append(doc.page_content)
    
    # doc_file_name = "CERT_C.json" if not cpp else "CERT_CPP.json"
    # if not cpp:
    #     os.makedirs(f"data/refined_raw_documents/CERT_C_faiss", exist_ok=True) 
    # else:
    #     os.makedirs(f"data/refined_raw_documents/CERT_CPP_faiss", exist_ok=True)
    # temp = "CERT_C_faiss" if not cpp else "CERT_CPP_faiss"
    # with open(f"data/refined_raw_documents/{temp}/{doc_file_name}", "w", encoding="utf-8") as f:
    #     json.dump(after_docs, f, indent=2, ensure_ascii=False)
    # print(f"Saved {len(after_docs)} documents to {doc_file_name}.")
    return split_docs


import re

def remove_spaced_words(text: str) -> str:
    """
    Remove spaced-out words like 'V a l i d a t i o n'
    """
    return re.sub(r'(?:\b[A-Za-z]\b\s+){2,}[A-Za-z]\b', '', text)


def load_js_sec_guides(file_path: str = "nodebestpractices/sections/security"):
    """
    Load JavaScript Secure Coding Guides from a directory.
    This will only load english markdown files.
    """
    loader = DirectoryLoader(
        file_path,
        glob="**/*.md",  # Load all markdown files first
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}, # Specify UTF-8 encoding
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    # Filter out translated files. English files have names like 'foo.md', 
    # translations are 'foo.lang.md'. We can filter by checking for dots in the file stem.
    english_docs = []
    for doc in documents:
        source_path = Path(doc.metadata['source'])
        if '.' not in source_path.stem:
            english_docs.append(doc)

    for doc in english_docs:
        doc.page_content = clean_markdown_full(doc.page_content)
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(english_docs)

    doc_file_name = "JavaScript.json" 
    os.makedirs(f"data/refined_raw_documents/JavaScript_faiss", exist_ok=True)
    with open(f"data/refined_raw_documents/JavaScript_faiss/{doc_file_name}", "w", encoding="utf-8") as f:
        json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(split_docs)} English documents from {file_path}.")
    return split_docs
    
def load_go_sec_guides(goscp_path: str, godev_url: str):
    """
    Load Go Secure Coding Guides from OWASP Go-SCP PDF and Go official documentation URL.
    """
    # 1. Load from OWASP Go-SCP PDF
    pdf_loader = PyPDFLoader(goscp_path)
    pdf_docs = pdf_loader.load()
    for doc in pdf_docs:
        doc.page_content = remove_spaced_words(doc.page_content)
    
    # 2. Load from go.dev/doc/security
    response = requests.get(godev_url)
    response.raise_for_status()
    # Use response.text to handle encoding based on HTTP headers
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the main content area by looking for the <article> tag
    main_content = soup.find('article')
    if not main_content:
        main_content = soup.find('body') # fallback to body
        
    text_content = main_content.get_text(separator='\n', strip=True)
    url_doc = Document(page_content=text_content, metadata={"source": godev_url})
    
    documents = pdf_docs + [url_doc]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(documents)
    split_docs = [
        doc for doc in split_docs
        if len(doc.page_content.strip()) >= 40
    ]
    split_docs = split_docs[1:]

    doc_file_name = "Go.json" 
    os.makedirs(f"data/refined_raw_documents/Go_faiss", exist_ok=True)
    with open(f"data/refined_raw_documents/Go_faiss/{doc_file_name}", "w", encoding="utf-8") as f:
        json.dump([doc.page_content for doc in split_docs], f, indent=2, ensure_ascii=False)
    
    print(f"Loaded {len(split_docs)} documents from Go sources.")
    return split_docs

def load_python_sec_guides(file_path: str = "../../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python"):
    """
    Load Python Secure Coding Guides from a directory.
    """
    loader = DirectoryLoader(
        file_path,
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True
    )
    documents = loader.load()
    for doc in documents:
        doc.page_content = clean_markdown_full(doc.page_content)
    # Clean and split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(documents)
    
    py_docs = []
    for i, doc in enumerate(split_docs):
        py_docs.append(doc.page_content)
    os.makedirs(f"data/refined_raw_documents/Python_faiss", exist_ok=True)
    with open("data/refined_raw_documents/Python_faiss/python.json", "w", encoding="utf-8") as f:
        json.dump(py_docs, f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(split_docs)} documents from {file_path}.")
    return split_docs

def load_owasp_cheat_sheets(file_path: str = "../../CheatSheetSeries/cheatsheets"):
    """
    Load OWASP Cheat Sheets from a directory.
    """
    loader = DirectoryLoader(
        file_path,
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True
    )
    documents = loader.load()
    
    for doc in documents:
        doc.page_content = clean_markdown_full(doc.page_content)
    # Clean and split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4500, chunk_overlap=600)
    split_docs = text_splitter.split_documents(documents)
    owasp_docs = []
    split_docs = [doc for doc in split_docs if len(doc.page_content) > 200]  # Filter out too short documents
    for i, doc in enumerate(split_docs):
        owasp_docs.append(doc.page_content)
    print(f"Loaded {len(split_docs)} documents from {file_path}.")
    # exit(1)
    os.makedirs(f"data/refined_raw_documents/OWASP_CheatSheets_faiss", exist_ok=True)
    with open("data/refined_raw_documents/OWASP_CheatSheets_faiss/owasp_cheatsheet_docs.json", "w", encoding="utf-8") as f:
        json.dump(owasp_docs, f, indent=2, ensure_ascii=False)
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

def make_vectorstore_from_documents(documents, save_path=None):
    """
    Create a FAISS vector store from a list of documents.
    """
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(documents, embedding)
    print(f"Vectorstore created with {len(documents)} documents.")
    if save_path:
        vectorstore.save_local(save_path)
    return vectorstore

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
        f"Description: {row.get('Description','')}",
        f"Extended Description: {row.get('Extended Description','')}",
        f"Mitigations: {row.get('Potential Mitigations','')}"
    ]
    return "\n".join(str(p) for p in parts if p)

def load_cwe_document(csv_path = '../data/rc_cwe_list.csv'):

    df_cwe_list = pd.read_csv(csv_path, index_col=False, header=0)
    selected_columns = [
        'CWE-ID',
        'Name',
        'Related Weaknesses',
        # 'Detection Methods',
        'Description',
        'Potential Mitigations',
    ]
    df_cwe_selected = df_cwe_list[selected_columns].copy()

    # Extract CWE IDs from each row's 'Related Weaknesses' and replace the column values with the list of IDs
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

if __name__ == "__main__":
    # pass
    
    # Flag to control database creation
    CREATE_DBS = True 

    if CREATE_DBS:

        # 2. Create JavaScript RAG base (skip if directory doesn't exist)
        # print("Creating JavaScript RAG database...")
        # js_docs = load_js_sec_guides("../nodebestpractices/sections/security")
        # # make_vectorstore_from_documents(js_docs, save_path="data/rag_databases/JavaScript_faiss")

        # # 3. Create Go RAG base (skip if PDF doesn't exist)
        # print("Creating Go RAG database...")
        # go_docs = load_go_sec_guides(
        #     goscp_path="../Go-SCP/dist/go-webapp-scp.pdf",
        #     godev_url="https://go.dev/doc/security/"
        # )
        # # make_vectorstore_from_documents(go_docs, save_path="data/rag_databases/Go_faiss")
        
        # python_docs = load_python_sec_guides("../wg-best-practices-os-developers/docs/Secure-Coding-Guide-for-Python")
        # print(f"Loaded {len(python_docs)} Python secure coding documents.")
        # # vectorstore = make_vectorstore_from_documents(python_docs, save_path="data/rag_databases/Python_faiss")

        # asvs_docs = load_ASVS_documents("data/OWASP Application Security Verification Standard 4.0.3-en.flat.json")
        # print(f"Loaded {len(asvs_docs)} ASVS documents.")
        # # vectorstore = make_vectorstore_from_documents(asvs_docs, save_path="data/rag_databases/ASVS_faiss")

        # cert_c_docs = load_CERT_C_documents("data/SEI CERT C Coding Standard_rules.pdf")
        # print(f"Loaded {len(cert_c_docs)} CERT C documents.")
        # # vectorstore = make_vectorstore_from_documents(cert_c_docs, save_path="data/rag_databases/CERT_C_faiss")
        
        cert_cpp_docs = load_CERT_C_documents("src/make_rag_base/SEI CERT CPP Coding Standard.pdf", cpp=True)
        print(f"Loaded {len(cert_cpp_docs)} CERT C++ documents.")
        # vectorstore = make_vectorstore_from_documents(cert_cpp_docs, save_path="data/rag_databases/CERT_CPP_faiss")

        # db_path = "../data/rag_databases/cwe_faiss"
        # docs = load_cwe_document()
        # vectorstore = make_vectorstore_from_documents(docs, save_path=db_path)

        # owasp_docs = load_owasp_cheat_sheets("../CheatSheetSeries/cheatsheets")
        # print(f"Loaded {len(owasp_docs)} OWASP CheatSheets documents.")
        # vectorstore = make_vectorstore_from_documents(owasp_docs, save_path="data/rag_databases/OWASP_CheatSheets_faiss")


#######

import json
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings


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
    """
    Create a FAISS vector store from a list of documents.
    """
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(documents, embedding)
    print(f"Vectorstore created with {len(documents)} documents.")

    if save_path:
        vectorstore.save_local(save_path)
        print(f"Saved FAISS index to: {save_path}")

    return vectorstore


def build_faiss_for_json(json_path: str):
    json_path = Path(json_path)
    base_dir = json_path.parent
    save_dir = base_dir / "faiss_index"

    print(f"\n[+] Processing: {json_path}")
    docs = load_documents_from_json(json_path)
    make_vectorstore_from_documents(docs, save_path=str(save_dir))


# if __name__ == "__main__":
#     # JSON_FILES = [
#     #     "../../data/refined_raw_documents/Go_faiss/Go_refined.json",
#     #     "../../data/refined_raw_documents/CERT_C_faiss/CERT_C_refined.json",
#     #     "../../data/refined_raw_documents/CERT_CPP_faiss/CERT_CPP_refined.json",
#     #     "../../data/refined_raw_documents/JavaScript_faiss/JavaScript_refined.json",
#     #     "../../data/refined_raw_documents/OWASP_CheatSheets_faiss/owasp_cheatsheet_docs_refined.json",
#     #     "../../data/refined_raw_documents/Python_faiss/python_refined.json",
#     # ]

#     # for json_file in JSON_FILES:
#     #     build_faiss_for_json(json_file)
