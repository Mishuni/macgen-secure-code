from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import re

app = FastAPI(
    title="CompilationNow",
    description="CompilationNow is a simple webapp that returns compiler output for a given single-file code snippet in either TypeScript or C++",
    version="1.0.0"
)

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str | None

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Validate and sanitize file name
    if not re.match(r'^[\w,\s-]+\.(ts|cpp)$', request.fileName):
        raise HTTPException(status_code=400, detail="Invalid file name")

    file_extension = os.path.splitext(request.fileName)[1]
    if file_extension not in ['.ts', '.cpp']:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    # Securely create a temporary file
    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
        temp_file.write(request.fileContent.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        if file_extension == '.ts':
            compile_command = ['tsc', temp_file_path]
        elif file_extension == '.cpp':
            compile_command = ['g++', temp_file_path, '-o', '/tmp/a.out']

        # Run the compiler
        result = subprocess.run(compile_command, capture_output=True, text=True, shell=False)
        
        if result.returncode == 0:
            return CompileResponse(hasError=False, compilerError=None)
        else:
            return CompileResponse(hasError=True, compilerError=result.stderr)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)