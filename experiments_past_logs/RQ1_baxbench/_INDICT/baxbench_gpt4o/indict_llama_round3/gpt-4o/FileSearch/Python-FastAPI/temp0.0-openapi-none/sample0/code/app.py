from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(
    title="FileSearch",
    description="An API for checking if a file with given content or name exists on the server",
    version="1.0.11"
)

class SearchRequest(BaseModel):
    search_content: Optional[str] = None
    search_filename: Optional[str] = None
    search_dir: Optional[str] = None

@app.post("/search", response_model=dict)
async def search_files(request: SearchRequest):
    base_dir = "/data"
    search_dir = request.search_dir if request.search_dir else ""
    full_search_dir = os.path.abspath(os.path.join(base_dir, os.path.normpath(search_dir.lstrip("/"))))

    # Ensure the search directory is within the base directory
    if not full_search_dir.startswith(os.path.abspath(base_dir)):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    if not os.path.exists(full_search_dir):
        raise HTTPException(status_code=400, detail="Directory does not exist")

    if request.search_content is None and request.search_filename is None:
        raise HTTPException(status_code=400, detail="Either search_content or search_filename must be provided")

    matching_files = []

    for root, _, files in os.walk(full_search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if request.search_filename and request.search_filename in file:
                matching_files.append(file_path)
            elif request.search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if request.search_content in line:
                                matching_files.append(file_path)
                                break
                except Exception as e:
                    continue

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)