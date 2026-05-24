from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import tempfile

app = FastAPI()

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str | None

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Determine the file extension
    file_extension = request.fileName.split('.')[-1]
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(request.fileContent.encode())
        temp_file_path = temp_file.name

    try:
        if file_extension == "cpp":
            # Compile C++ code
            compile_command = ["g++", temp_file_path, "-o", "/tmp/output"]
            result = subprocess.run(compile_command, capture_output=True, text=True)
            if result.returncode != 0:
                return CompileResponse(hasError=True, compilerError=result.stderr.strip())
            else:
                return CompileResponse(hasError=False, compilerError=None)

        elif file_extension == "ts":
            # Compile TypeScript code
            compile_command = ["tsc", temp_file_path]
            result = subprocess.run(compile_command, capture_output=True, text=True)
            if result.returncode != 0:
                return CompileResponse(hasError=True, compilerError=result.stderr.strip())
            else:
                return CompileResponse(hasError=False, compilerError=None)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only .cpp and .ts are allowed.")

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)