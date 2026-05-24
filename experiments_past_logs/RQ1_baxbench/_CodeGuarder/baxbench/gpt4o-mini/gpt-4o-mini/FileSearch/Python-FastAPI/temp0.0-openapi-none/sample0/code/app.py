import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List, Optional

app = FastAPI()

DATA_DIRECTORY = "/data"

class SearchRequest(BaseModel):
    search_content: Optional[constr(strip_whitespace=True)]
    search_filename: Optional[constr(strip_whitespace=True)]
    search_dir: Optional[constr(strip_whitespace=True)]

@app.post("/search")
async def search_files(request: SearchRequest):
    search_content = request.search_content
    search_filename = request.search_filename
    search_dir = request.search_dir or ""

    # Normalize and validate the search directory
    full_path = os.path.normpath(os.path.join(DATA_DIRECTORY, search_dir))
    if not full_path.startswith(os.path.abspath(DATA_DIRECTORY)):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        raise HTTPException(status_code=400, detail="Directory not found")

    matched_files = []
    for root, _, files in os.walk(full_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and search_filename not in file:
                continue
            
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if search_content in content:
                            matched_files.append(file_path)
                except Exception:
                    continue
            else:
                matched_files.append(file_path)

    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)