from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI()

class SearchRequest(BaseModel):
    search_content: Optional[str] = None
    search_filename: Optional[str] = None
    search_dir: Optional[str] = None

@app.post("/search")
async def search_files(request: SearchRequest):
    base_dir = "/data"
    search_dir = request.search_dir if request.search_dir else ""
    target_dir = os.path.join(base_dir, search_dir.lstrip("/"))

    # Validate directory path to prevent directory traversal
    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        raise HTTPException(status_code=400, detail="Invalid directory")
    if not os.path.commonpath([base_dir, target_dir]).startswith(base_dir):
        raise HTTPException(status_code=400, detail="Directory traversal attempt detected")

    matching_files = []

    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if request.search_filename and file.startswith(request.search_filename):
                matching_files.append(file_path)
            elif request.search_content:
                try:
                    # Check file size to prevent resource exhaustion
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB limit
                        continue
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if request.search_content in f.read():
                            matching_files.append(file_path)
                except Exception:
                    continue

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)