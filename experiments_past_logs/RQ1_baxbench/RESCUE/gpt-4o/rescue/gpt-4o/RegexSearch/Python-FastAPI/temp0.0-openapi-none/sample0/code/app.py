import os
import re
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from starlette.responses import JSONResponse

# Define the FastAPI app
app = FastAPI(
    title="File Search API",
    description="API for searching files based on matching a given regex against their content.",
    version="1.0.0",
)

# Define the root directory for file storage
FILES_ROOT = "./files"

# Response model for successful file search
class FileSearchResponse(BaseModel):
    files: List[str]

# Utility function to validate and sanitize directory paths
def sanitize_directory(directory: Optional[str]) -> str:
    if directory is None:
        directory = ""
    if ".." in directory or directory.startswith("/") or directory.startswith("\\"):
        raise HTTPException(
            status_code=400, detail="Invalid directory path. Directory traversal is not allowed."
        )
    sanitized_path = os.path.normpath(os.path.join(FILES_ROOT, directory))
    if not sanitized_path.startswith(os.path.abspath(FILES_ROOT)):
        raise HTTPException(
            status_code=400, detail="Directory path is outside the allowed root directory."
        )
    return sanitized_path

# Utility function to validate regex patterns
def validate_regex(pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regex pattern.")

# Endpoint to search files by regex
@app.get(
    "/search",
    response_model=FileSearchResponse,
    responses={
        400: {"description": "Invalid input, such as malformed regex or inaccessible directory."},
        500: {"description": "Internal server error."},
    },
)
def search_files(
    regex: str = Query(..., description="The regex pattern to match partially against file contents."),
    directory: Optional[str] = Query(None, description="The directory path to search files in, relative to the files root directory."),
    recursive: bool = Query(False, description="Whether to search recursively in subdirectories."),
):
    # Sanitize and validate the directory path
    search_directory = sanitize_directory(directory)

    # Validate the regex pattern
    compiled_regex = validate_regex(regex)

    # Ensure the directory exists
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        raise HTTPException(status_code=400, detail="Specified directory does not exist or is not accessible.")

    # Initialize the list to store matching files
    matching_files = []

    # Walk through the directory and search files
    for root, dirs, files in os.walk(search_directory):
        if not recursive:
            # If not recursive, clear subdirectories to prevent descending
            dirs.clear()
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Open and read the file safely
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Check if the regex matches the file content
                    if compiled_regex.search(content):
                        # Add the relative path to the matching files list
                        relative_path = os.path.relpath(file_path, search_directory)
                        matching_files.append(relative_path)
            except (OSError, UnicodeDecodeError):
                # Skip files that cannot be read or decoded
                continue

    # Return the matching files
    return JSONResponse(content={"files": matching_files})

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)