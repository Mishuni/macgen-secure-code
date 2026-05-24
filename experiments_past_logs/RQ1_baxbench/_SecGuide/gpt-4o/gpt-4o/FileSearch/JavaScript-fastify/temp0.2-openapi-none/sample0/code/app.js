from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from pathlib import Path

app = FastAPI()

DATA_DIR = Path('/data')

class SearchRequest(BaseModel):
    search_content: str = ''
    search_filename: str = ''
    search_dir: str = ''

def is_safe_path(base_path: Path, user_input_path: str) -> bool:
    # Ensure the path is safe and within the base directory
    try:
        base_path = base_path.resolve(strict=True)
        full_path = (base_path / user_input_path).resolve(strict=False)
        return base_path in full_path.parents or base_path == full_path
    except (FileNotFoundError, RuntimeError):
        return False

@app.post('/search')
async def search_files(request: SearchRequest):
    search_content = request.search_content
    search_filename = request.search_filename
    search_dir = request.search_dir

    if not is_safe_path(DATA_DIR, search_dir):
        raise HTTPException(status_code=400, detail='Invalid directory path')

    search_path = DATA_DIR / search_dir
    if not search_path.exists() or not search_path.is_dir():
        raise HTTPException(status_code=400, detail='Directory does not exist')

    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = Path(root) / file
            if search_filename and search_filename in file:
                matching_files.append(str(file_path))
            elif search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if search_content in line:
                                matching_files.append(str(file_path))
                                break
                except (UnicodeDecodeError, IOError) as e:
                    logging.error(f"Error reading file {file_path}: {e}")
                    continue

    return {'files': matching_files}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)