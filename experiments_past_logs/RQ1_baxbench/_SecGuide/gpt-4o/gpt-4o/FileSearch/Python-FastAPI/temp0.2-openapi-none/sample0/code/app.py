from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import os
import logging

app = FastAPI()

# Define the base directory for file searches
BASE_DIR = "/data"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic model for request body
class SearchRequest(BaseModel):
    search_content: Optional[str] = None
    search_filename: Optional[str] = None
    search_dir: Optional[str] = None

def is_safe_path(base_path: str, user_input_path: str) -> bool:
    # Ensure the user input path is safe and within the base directory
    try:
        # Resolve symbolic links and get the canonical path
        absolute_path = os.path.realpath(os.path.join(base_path, user_input_path))
        return os.path.commonpath([base_path, absolute_path]) == os.path.realpath(base_path)
    except Exception as e:
        logger.error("Error resolving path")
        return False

@app.post("/search")
async def search_files(request: SearchRequest):
    search_dir = request.search_dir or ""
    
    # Validate the search directory
    if not is_safe_path(BASE_DIR, search_dir):
        raise HTTPException(status_code=400, detail="Invalid search directory")

    # Construct the full search path
    full_search_path = os.path.join(BASE_DIR, search_dir)

    # Initialize the list to store matching files
    matching_files = []

    # Walk through the directory
    for root, _, files in os.walk(full_search_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if the filename matches
            if request.search_filename and request.search_filename in file:
                matching_files.append(file_path)
                continue

            # Check if the file content matches
            if request.search_content:
                try:
                    # Limit the size of the file to read
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if request.search_content in line:
                                matching_files.append(file_path)
                                break
                except Exception:
                    logger.error("Error reading file")
                    continue

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)