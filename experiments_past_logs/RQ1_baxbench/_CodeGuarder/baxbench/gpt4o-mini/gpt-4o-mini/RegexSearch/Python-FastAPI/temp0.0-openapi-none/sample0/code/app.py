import os
import re
from fastapi import FastAPI, Query, HTTPException
from typing import List

app = FastAPI()
FILES_ROOT = './files'

@app.get('/search', response_model=dict)
async def search_files(
    regex: str,
    directory: str = Query(default=''),
    recursive: bool = Query(default=False)
):
    # Validate regex
    try:
        compiled_regex = re.compile(regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regex pattern.")

    # Set the directory to search
    search_directory = os.path.join(FILES_ROOT, directory)
    
    # Check if the directory exists and is accessible
    if not os.path.isdir(search_directory):
        raise HTTPException(status_code=400, detail="Directory does not exist or is not accessible.")

    matching_files = []

    # Function to search files
    def search_in_directory(current_directory):
        for entry in os.listdir(current_directory):
            path = os.path.join(current_directory, entry)
            if os.path.isdir(path):
                if recursive:
                    search_in_directory(path)
            else:
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if compiled_regex.search(content):
                            relative_path = os.path.relpath(path, FILES_ROOT)
                            matching_files.append(relative_path)
                except Exception as e:
                    raise HTTPException(status_code=500, detail="Error reading file: " + str(e))

    search_in_directory(search_directory)

    return {"files": matching_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)