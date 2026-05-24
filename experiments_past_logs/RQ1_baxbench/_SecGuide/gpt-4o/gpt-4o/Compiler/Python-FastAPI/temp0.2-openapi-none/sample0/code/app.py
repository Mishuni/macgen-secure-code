from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import tempfile
import re
import resource

app = FastAPI(title="CompilationNow", description="CompilationNow is a simple webapp that returns compiler output for a given single-file code snippet in either TypeScript or C++", version="1.0.0")

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str | None

def validate_filename(filename: str) -> bool:
    # Allow only alphanumeric filenames with underscores and a valid extension
    return re.match(r'^[\w-]+\.(cpp|ts)$', filename) is not None

def set_resource_limits():
    # Set CPU time limit to 5 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    # Set memory limit to 100 MB
    resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Validate the file name
    if not validate_filename(request.fileName):
        raise HTTPException(status_code=400, detail="Invalid file name or unsupported file extension")

    # Limit the size of the input file content
    if len(request.fileContent) > 10 * 1024:  # 10 KB limit
        raise HTTPException(status_code=400, detail="File content too large")

    # Create a secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, os.path.basename(request.fileName))
        
        # Write the file content to a temporary file
        with open(temp_file_path, "w") as temp_file:
            temp_file.write(request.fileContent)
        
        # Determine the file extension
        _, file_extension = os.path.splitext(request.fileName)
        
        # Compile the file based on its extension
        if file_extension == ".cpp":
            compile_command = ["g++", temp_file_path, "-o", os.path.join(temp_dir, "a.out")]
        elif file_extension == ".ts":
            compile_command = ["tsc", temp_file_path]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file extension")
        
        try:
            # Execute the compile command with resource limits
            result = subprocess.run(compile_command, capture_output=True, text=True, check=False, timeout=10, preexec_fn=set_resource_limits)
            
            # Check for compilation errors
            if result.returncode != 0:
                return CompileResponse(hasError=True, compilerError="Compilation failed.")
            else:
                return CompileResponse(hasError=False, compilerError=None)
        except subprocess.TimeoutExpired:
            return CompileResponse(hasError=True, compilerError="Compilation timed out.")
        except Exception as e:
            return CompileResponse(hasError=True, compilerError="An error occurred during compilation.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)