from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import os
import re

app = FastAPI(
    title="File Search API",
    description="API for searching files based on matching a given regex against their content.",
    version="1.0.0"
)

FILES_ROOT = "./files"

def is_safe_path(base_path: str, path: str) -> bool:
    # Ensure the path is within the base directory
    return os.path.realpath(path).startswith(os.path.realpath(base_path))

@app.get("/search", summary="Search files by regex")
async def search_files(
    regex: str = Query(..., description="The regex pattern to match partially against file contents."),
    directory: Optional[str] = Query(None, description="The directory path to search files in, relative to the files root directory."),
    recursive: bool = Query(False, description="Whether to search recursively in subdirectories.")
) -> dict:
    search_path = os.path.join(FILES_ROOT, directory) if directory else FILES_ROOT

    if not is_safe_path(FILES_ROOT, search_path) or not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Invalid directory path.")

    try:
        compiled_regex = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Malformed regex pattern.")

    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if compiled_regex.search(content):
                        relative_path = os.path.relpath(file_path, search_path)
                        matching_files.append(relative_path)
            except Exception as e:
                continue

        if not recursive:
            break

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)