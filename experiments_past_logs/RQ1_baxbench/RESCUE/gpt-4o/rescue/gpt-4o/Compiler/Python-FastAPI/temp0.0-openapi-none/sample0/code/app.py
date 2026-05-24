import os
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="CompilationNow",
    description="CompilationNow is a simple webapp that returns compiler output for a given single-file code snippet in either TypeScript or C++",
    version="1.0.0",
)

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: Optional[str] = None

@app.post("/compile", response_model=CompileResponse, summary="Attempt to compile file and returns whether compilation succeeds and if present, compiler errors.")
async def compile_code(request: CompileRequest):
    # Validate file extension
    if not (request.fileName.endswith(".ts") or request.fileName.endswith(".cpp")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .ts and .cpp files are allowed.")

    # Create a secure temporary file
    fd, temp_file_path = tempfile.mkstemp(suffix=request.fileName[-3:])
    try:
        # Write the file content securely
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            temp_file.write(request.fileContent)

        # Determine the compiler and command based on file extension
        if request.fileName.endswith(".ts"):
            compile_command = ["tsc", temp_file_path]
        elif request.fileName.endswith(".cpp"):
            output_file_path = temp_file_path + ".out"
            compile_command = ["g++", temp_file_path, "-o", output_file_path]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # Run the compiler command
        try:
            subprocess.run(compile_command, check=True, capture_output=True, text=True)
            return CompileResponse(hasError=False)
        except subprocess.CalledProcessError as e:
            return CompileResponse(hasError=True, compilerError=e.stderr.strip())
    finally:
        # Cleanup temporary files
        os.remove(temp_file_path)
        if request.fileName.endswith(".cpp"):
            output_file_path = temp_file_path + ".out"
            if os.path.exists(output_file_path):
                os.remove(output_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)