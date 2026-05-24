from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import os

# Constants
DATA_DIR = "/data"

# FastAPI app initialization
app = FastAPI(
    title="FileSearch",
    description="An API for checking if a file with given content or name exists on the server",
    version="1.0.11"
)

# Request body model
class SearchRequest(BaseModel):
    search_content: Optional[str] = Field(None, example="Hello World")
    search_filename: Optional[str] = Field(None, example="file.txt")
    search_dir: Optional[str] = Field(None, example="/songs")

# Utility function to sanitize and validate directory paths
def sanitize_and_validate_path(base_dir: str, user_path: Optional[str]) -> str:
    if user_path is None:
        return base_dir
    abs_path = os.path.abspath(os.path.join(base_dir, user_path.lstrip("/")))
    if not abs_path.startswith(base_dir):
        raise ValueError("Invalid directory path")
    return abs_path

# Utility function to search for files
def search_files(base_dir: str, search_content: Optional[str], search_filename: Optional[str]) -> List[str]:
    matching_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Match filename
            if search_filename and search_filename in file:
                matching_files.append(file_path)
                continue
            # Match file content
            if search_content:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if search_content in f.read():
                            matching_files.append(file_path)
                except (UnicodeDecodeError, OSError):
                    # Skip binary or unreadable files
                    continue
    return matching_files

# POST /search endpoint
@app.post("/search", response_model=dict)
async def search(request: SearchRequest):
    try:
        # Sanitize and validate the search directory
        base_dir = sanitize_and_validate_path(DATA_DIR, request.search_dir)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Ensure at least one search parameter is provided
    if not request.search_content and not request.search_filename:
        raise HTTPException(status_code=400, detail="At least one of 'search_content' or 'search_filename' must be provided")

    # Perform the search
    try:
        matching_files = search_files(base_dir, request.search_content, request.search_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while searching for files")

    return {"files": matching_files}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)