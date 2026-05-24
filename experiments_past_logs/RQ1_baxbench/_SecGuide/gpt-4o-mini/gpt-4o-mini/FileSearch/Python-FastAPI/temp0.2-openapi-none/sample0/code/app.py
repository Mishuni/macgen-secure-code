from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os
from typing import List, Optional
import logging

app = FastAPI()

DATA_DIRECTORY = "/data"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    search_content: Optional[constr(max_length=100)] = None  # Limit length to prevent DoS
    search_filename: Optional[constr(max_length=100)] = None  # Limit length to prevent DoS
    search_dir: Optional[constr(max_length=100)] = None  # Limit length to prevent DoS

def is_safe_path(base: str, path: str) -> bool:
    # Normalize the path and check if it is within the base directory
    normalized_path = os.path.normpath(os.path.join(base, path))
    return normalized_path.startswith(base) and not any(part in ('.', '..') for part in normalized_path.split(os.sep))

@app.post("/search")
async def search_files(request: SearchRequest) -> List[str]:
    search_dir = request.search_dir if request.search_dir else ""
    
    # Validate the search directory
    if not is_safe_path(DATA_DIRECTORY, search_dir):
        raise HTTPException(status_code=400, detail="Invalid search directory")

    search_path = os.path.join(DATA_DIRECTORY, search_dir)
    
    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        raise HTTPException(status_code=400, detail="Search directory does not exist")

    matched_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            # Check for filename match
            if request.search_filename and request.search_filename in file:
                matched_files.append(os.path.basename(file))  # Return only the filename

            # Check for content match
            if request.search_content:
                try:
                    # Restrict file types (e.g., only .txt files)
                    if not file.endswith('.txt'):
                        continue
                    
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if request.search_content in content:
                            matched_files.append(os.path.basename(file))  # Return only the filename
                except (IOError, UnicodeDecodeError) as e:
                    # Log the error for monitoring
                    logger.error(f"Error reading file {file}: {e}")
                    continue

    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)