from fastapi import FastAPI, Query, HTTPException
import os
import re
from typing import List, Optional
import logging

app = FastAPI()

# Use an environment variable for the file root path
FILES_ROOT = os.getenv('FILES_ROOT', './files')

# Configure logging
logging.basicConfig(level=logging.INFO)

def validate_directory(directory: Optional[str]) -> str:
    if directory is None:
        return FILES_ROOT
    # Validate the directory input
    if not re.match(r'^[\w\-_.]+$', directory):
        raise HTTPException(status_code=400, detail="Invalid directory path.")
    full_path = os.path.join(FILES_ROOT, directory)
    if not full_path.startswith(os.path.abspath(FILES_ROOT)):
        raise HTTPException(status_code=400, detail="Directory traversal attempt detected.")
    return full_path

def search_files(regex: str, directory: str, recursive: bool) -> List[str]:
    matched_files = []
    
    # Limit regex complexity
    if len(regex) > 100:  # Example limit, adjust as necessary
        raise HTTPException(status_code=400, detail="Regex pattern too complex.")
    
    try:
        pattern = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Malformed regex pattern.")

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern.search(content):
                            matched_files.append(os.path.relpath(file_path, start=FILES_ROOT))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if pattern.search(content):
                        matched_files.append(os.path.relpath(file_path, start=FILES_ROOT))

    return matched_files

@app.get("/search", response_model=dict)
async def search(regex: str, directory: Optional[str] = Query(None), recursive: bool = Query(False)):
    try:
        validated_directory = validate_directory(directory)
        if not os.path.exists(validated_directory):
            raise HTTPException(status_code=400, detail="Directory does not exist.")
        matched_files = search_files(regex, validated_directory, recursive)
        return {"files": matched_files}
    except Exception as e:
        logging.error("Error occurred: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)