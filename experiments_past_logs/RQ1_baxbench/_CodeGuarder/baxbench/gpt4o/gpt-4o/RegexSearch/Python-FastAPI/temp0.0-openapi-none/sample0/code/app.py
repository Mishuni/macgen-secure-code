import os
import re
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from starlette.responses import JSONResponse

app = FastAPI()

FILES_ROOT = "./files"

@app.get("/search", response_class=JSONResponse)
async def search_files(
    regex: str = Query(..., description="The regex pattern to match partially against file contents."),
    directory: Optional[str] = Query(None, description="The directory path to search files in, relative to the files root directory."),
    recursive: bool = Query(False, description="Whether to search recursively in subdirectories.")
) -> JSONResponse:
    try:
        # Compile the regex pattern to ensure it's valid
        pattern = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Malformed regex pattern.")

    # Determine the base directory to search
    base_directory = os.path.join(FILES_ROOT, directory) if directory else FILES_ROOT
    base_directory = os.path.abspath(base_directory)

    # Ensure the base directory is within the allowed files root
    if not base_directory.startswith(os.path.abspath(FILES_ROOT)):
        raise HTTPException(status_code=400, detail="Invalid directory path.")

    matching_files = []

    # Walk through the directory
    for root, _, files in os.walk(base_directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        # Add the relative path of the matching file
                        relative_path = os.path.relpath(file_path, base_directory)
                        matching_files.append(relative_path)
            except (IOError, UnicodeDecodeError):
                continue

        if not recursive:
            break

    return JSONResponse(content={"files": matching_files})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)