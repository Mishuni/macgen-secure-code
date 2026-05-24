from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import subprocess
import os
import re

app = FastAPI()

class CompileRequest(BaseModel):
    fileName: constr(regex=r'^[a-zA-Z0-9_.-]+$')  # Only allow alphanumeric, underscores, hyphens, and periods
    fileContent: str

@app.post("/compile")
async def compile_code(request: CompileRequest):
    file_extension = request.fileName.split('.')[-1]
    if file_extension not in ['ts', 'cpp']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only TypeScript and C++ are allowed.")

    # Create a temporary file in a secure directory
    temp_file_path = f"/tmp/{request.fileName}"
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(request.fileContent)

    try:
        if file_extension == 'ts':
            # Compile TypeScript
            result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
        else:
            # Compile C++
            result = subprocess.run(['g++', temp_file_path, '-o', '/tmp/output'], capture_output=True, text=True)

        if result.returncode != 0:
            return {"hasError": True, "compilerError": result.stderr.strip()}
        else:
            return {"hasError": False, "compilerError": None}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)