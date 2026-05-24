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

@app.get("/search", summary="Search files by regex", description="Searches files in a specified directory and returns files whose content matches the given regex.")
async def search_files(
    regex: str = Query(..., description="The regex pattern to match partially against file contents, i.e. some part of the file content must match the regex.", max_length=100),
    directory: Optional[str] = Query(None, description="The directory path to search files in, relative to the files root directory."),
    recursive: bool = Query(False, description="Whether to search recursively in subdirectories.")
) -> dict:
    try:
        pattern = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regex pattern.")

    search_dir = os.path.join(FILES_ROOT, directory) if directory else FILES_ROOT
    resolved_path = os.path.realpath(search_dir)
    if not resolved_path.startswith(os.path.realpath(FILES_ROOT)):
        raise HTTPException(status_code=400, detail="Invalid directory path.")

    if not os.path.exists(search_dir) or not os.path.isdir(search_dir):
        raise HTTPException(status_code=400, detail="Directory does not exist or is not accessible.")

    matching_files = []

    for root, _, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        relative_path = os.path.relpath(file_path, search_dir)
                        matching_files.append(relative_path)
            except (IOError, UnicodeDecodeError):
                continue

        if not recursive:
            break

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)