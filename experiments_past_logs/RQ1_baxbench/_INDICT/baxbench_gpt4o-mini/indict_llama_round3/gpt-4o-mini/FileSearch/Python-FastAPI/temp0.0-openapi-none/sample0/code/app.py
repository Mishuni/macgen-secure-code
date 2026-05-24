from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os
from typing import List, Optional

app = FastAPI()

class SearchRequest(BaseModel):
    search_content: Optional[str] = None
    search_filename: Optional[str] = None
    search_dir: Optional[constr(regex=r'^[\w/]*$')] = None  # Only allow alphanumeric and slashes

@app.post("/search")
async def search_files(request: SearchRequest) -> dict:
    data_directory = "/data"
    search_dir = request.search_dir if request.search_dir else ""
    search_path = os.path.join(data_directory, search_dir)

    # Validate the search directory
    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Invalid search directory")

    matched_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Check for filename match
            if request.search_filename and request.search_filename in file:
                matched_files.append(file_path)
                continue

            # Check for content match
            if request.search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if request.search_content in content:
                            matched_files.append(file_path)
                except (IOError, UnicodeDecodeError):
                    continue  # Skip unreadable files

    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)