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
        raise HTTPException(status_code=400, detail="Invalid file extension. Only .ts and .cpp are allowed.")

    # Create a temporary file
    file_path = f"/tmp/{request.fileName}"
    try:
        with open(file_path, 'w') as f:
            f.write(request.fileContent)

        # Compile the code based on the file extension
        if request.fileName.endswith('.ts'):
            result = subprocess.run(['tsc', file_path], capture_output=True, text=True)
        else:  # C++
            result = subprocess.run(['g++', file_path, '-o', '/tmp/output'], capture_output=True, text=True)

        # Check for compilation errors
        if result.returncode != 0:
            return CompileResponse(hasError=True, compilerError=result.stderr.strip())
        return CompileResponse(hasError=False, compilerError=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during compilation.")
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)