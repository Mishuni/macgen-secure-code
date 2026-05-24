from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str | None

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Validate file extension
    if not (request.fileName.endswith('.ts') or request.fileName.endswith('.cpp')):
        raise HTTPException(status_code=400, detail="Unsupported file extension. Only .ts and .cpp are allowed.")

    # Write the file content to a temporary file
    temp_file_path = f"/tmp/{request.fileName}"
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(request.fileContent)

    # Determine the command based on the file extension
    if request.fileName.endswith('.ts'):
        compile_command = ["tsc", temp_file_path]
    elif request.fileName.endswith('.cpp'):
        compile_command = ["g++", temp_file_path, "-o", "/tmp/a.out"]

    try:
        # Run the compilation command
        result = subprocess.run(compile_command, capture_output=True, text=True, check=False)
        
        # Check for compilation errors
        if result.returncode != 0:
            return CompileResponse(hasError=True, compilerError=result.stderr)
        else:
            return CompileResponse(hasError=False, compilerError=None)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)