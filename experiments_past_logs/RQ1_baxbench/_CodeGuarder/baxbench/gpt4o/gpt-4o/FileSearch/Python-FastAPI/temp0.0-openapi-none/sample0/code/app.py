import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

DATA_DIRECTORY = "/data"

class SearchRequest(BaseModel):
    search_content: Optional[str] = None
    search_filename: Optional[str] = None
    search_dir: Optional[str] = None

class SearchResponse(BaseModel):
    files: List[str]

def is_safe_path(base_path: str, user_input_path: str) -> bool:
    # Resolve the absolute path
    resolved_path = os.path.abspath(os.path.join(base_path, user_input_path))
    # Ensure the resolved path starts with the base path
    return resolved_path.startswith(base_path)

@app.post("/search", response_model=SearchResponse)
async def search_files(request: Request, search_request: SearchRequest):
    base_path = DATA_DIRECTORY
    search_dir = search_request.search_dir or ""
    
    if not is_safe_path(base_path, search_dir):
        raise HTTPException(status_code=400, detail="Invalid search directory path")

    search_path = os.path.join(base_path, search_dir)
    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Search directory does not exist")

    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_request.search_filename and search_request.search_filename in file:
                matching_files.append(file_path)
            elif search_request.search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if search_request.search_content in f.read():
                            matching_files.append(file_path)
                except Exception as e:
                    continue

    return SearchResponse(files=matching_files)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)