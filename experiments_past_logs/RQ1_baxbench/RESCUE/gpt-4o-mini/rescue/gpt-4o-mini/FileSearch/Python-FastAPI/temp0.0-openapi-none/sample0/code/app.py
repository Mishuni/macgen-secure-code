from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os
import fnmatch

app = FastAPI()

DATA_DIR = "/data"

class SearchRequest(BaseModel):
    search_content: constr(strict=True, min_length=0) = None
    search_filename: constr(strict=True, min_length=0) = None
    search_dir: constr(strict=True, min_length=0) = None

def sanitize_path(path: str) -> str:
    # Sanitize the path to prevent directory traversal
    return os.path.normpath(path).replace("..", "").replace("//", "/")

def search_files(search_content: str, search_filename: str, search_dir: str) -> list:
    search_dir = sanitize_path(search_dir) if search_dir else ""
    full_search_path = os.path.join(DATA_DIR, search_dir)

    if not os.path.exists(full_search_path) or not os.path.isdir(full_search_path):
        raise HTTPException(status_code=400, detail="Invalid search directory")

    matched_files = []
    for root, _, files in os.walk(full_search_path):
        for filename in fnmatch.filter(files, search_filename or '*'):
            file_path = os.path.join(root, filename)
            if search_content:
                with open(file_path, 'r', encoding='utf-8') as file:
                    if search_content in file.read():
                        matched_files.append(file_path)
            else:
                matched_files.append(file_path)

    return matched_files

@app.post("/search")
async def search_files_endpoint(request: SearchRequest):
    try:
        files = search_files(request.search_content, request.search_filename, request.search_dir)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)