import os
import re
from fastapi import FastAPI, HTTPException
from typing import List, Optional

app = FastAPI()
FILES_ROOT = './files'

@app.get("/search")
def search_files(regex: str, directory: Optional[str] = None, recursive: Optional[bool] = False) -> dict:
    if directory is not None:
        if '..' in directory.split(os.sep):
            raise HTTPException(status_code=400, detail="Invalid directory path.")
        search_path = os.path.join(FILES_ROOT, directory)
        if not os.path.commonpath([search_path, FILES_ROOT]) == FILES_ROOT:
            raise HTTPException(status_code=400, detail="Invalid directory path.")
    else:
        search_path = FILES_ROOT

    if re.search(r'(\(\?P<\w+>|\(\?=\w+|\(\?<!\w+)', regex):
        raise HTTPException(status_code=400, detail="Complex regex pattern not allowed.")

    matched_files = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.startswith(FILES_ROOT):
                continue
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if re.search(regex, content):
                    matched_files.append(os.path.relpath(file_path, start=search_path))
        if not recursive:
            break

    return {"files": matched_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)