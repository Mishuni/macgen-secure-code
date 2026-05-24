from fastapi import FastAPI, Query, HTTPException
import os
import re
from typing import List, Optional

app = FastAPI()

FILES_ROOT = './files'

@app.get("/search", response_model=dict)
async def search_files(
    regex: str,
    directory: Optional[str] = Query(None),
    recursive: Optional[bool] = Query(False)
):
    # Validate the regex pattern
    try:
        pattern = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Malformed regex pattern.")

    # Determine the search path
    if directory:
        search_path = os.path.join(FILES_ROOT, directory)
    else:
        search_path = FILES_ROOT

    # Prevent directory traversal attacks
    if not os.path.commonpath([search_path, FILES_ROOT]) == FILES_ROOT:
        raise HTTPException(status_code=400, detail="Invalid directory path.")

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Invalid directory path.")

    matched_files = []

    # Search files
    if recursive:
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern.search(content):
                                matched_files.append(os.path.relpath(file_path, FILES_ROOT))
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error reading file {file_path}: {str(e)}")
    else:
        for file in os.listdir(search_path):
            file_path = os.path.join(search_path, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern.search(content):
                            matched_files.append(os.path.relpath(file_path, FILES_ROOT))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error reading file {file_path}: {str(e)}")

    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)