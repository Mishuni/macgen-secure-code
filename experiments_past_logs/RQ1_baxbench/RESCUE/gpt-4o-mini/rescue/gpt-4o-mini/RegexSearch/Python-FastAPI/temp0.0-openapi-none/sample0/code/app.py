from fastapi import FastAPI, Query, HTTPException
import os
import re
from typing import List, Optional

app = FastAPI()

# Define the root directory for file searches
FILES_ROOT = './files'

def sanitize_directory(directory: str) -> str:
    # Sanitize the directory input to prevent directory traversal
    if '..' in directory or directory.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid directory path.")
    return os.path.normpath(directory)

def search_files(regex: str, directory: str, recursive: bool) -> List[str]:
    # Compile the regex pattern
    try:
        pattern = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Malformed regex pattern.")

    # Sanitize and validate the directory
    directory = sanitize_directory(directory)
    search_path = os.path.join(FILES_ROOT, directory)

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Directory does not exist or is not accessible.")

    matched_files = []

    # Search files in the specified directory
    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        # Store the file path relative to the search directory
                        relative_path = os.path.relpath(file_path, search_path)
                        matched_files.append(relative_path)
            except (IOError, UnicodeDecodeError):
                # Handle files that cannot be read
                continue

        if not recursive:
            break  # Stop searching deeper if not recursive

    return matched_files

@app.get("/search")
async def search(regex: str, directory: Optional[str] = Query("", max_length=255), recursive: bool = Query(False)):
    # Default to the root directory if none is provided
    if not directory:
        directory = ""

    matched_files = search_files(regex, directory, recursive)
    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)