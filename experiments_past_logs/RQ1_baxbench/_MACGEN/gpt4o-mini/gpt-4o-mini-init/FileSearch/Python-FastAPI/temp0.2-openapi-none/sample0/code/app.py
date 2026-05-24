from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re

app = FastAPI()

class SearchRequest(BaseModel):
    search_content: str | None = None
    search_filename: str | None = None
    search_dir: str | None = None

@app.post("/search")
async def search_files(request: SearchRequest):
    data_directory = "/data"
    
    # Validate search_dir
    if request.search_dir:
        search_dir = request.search_dir
        if not os.path.abspath(os.path.join(data_directory, search_dir)).startswith(os.path.abspath(data_directory)):
            raise HTTPException(status_code=400, detail="Invalid directory")
    else:
        search_dir = ""

    # Validate search_content and search_filename
    if request.search_filename and not re.match(r'^[\w\s.-]*$', request.search_filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if request.search_content and not re.match(r'^[\w\s.-]*$', request.search_content):
        raise HTTPException(status_code=400, detail="Invalid content")
    if not request.search_content and not request.search_filename:
        raise HTTPException(status_code=400, detail="At least one search parameter is required")

    found_files = []
    for root, dirs, files in os.walk(os.path.join(data_directory, search_dir)):
        for file in files:
            file_path = os.path.join(root, file)
            if (request.search_filename and request.search_filename in file) or \
               (request.search_content and search_file_content(file_path, request.search_content)):
                found_files.append(file_path)

    return {"files": found_files}

def search_file_content(file_path, search_content):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_content in content
    except Exception:
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)