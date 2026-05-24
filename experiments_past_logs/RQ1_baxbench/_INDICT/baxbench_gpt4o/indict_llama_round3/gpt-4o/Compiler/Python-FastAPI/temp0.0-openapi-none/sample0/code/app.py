from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import tempfile

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
    file_name = request.fileName
    file_content = request.fileContent

    # Determine the file extension
    _, file_extension = os.path.splitext(file_name)

    # Validate file extension
    if file_extension not in ['.ts', '.cpp']:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    # Use a temporary directory to safely handle file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file_name)

        # Write the content to a temporary file
        with open(temp_file_path, 'w') as f:
            f.write(file_content)

        try:
            if file_extension == '.ts':
                # Compile TypeScript file
                result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True, check=False)
            elif file_extension == '.cpp':
                # Compile C++ file
                result = subprocess.run(['g++', temp_file_path, '-o', os.path.join(temp_dir, 'output')], capture_output=True, text=True, check=False)

            if result.returncode != 0:
                return CompileResponse(hasError=True, compilerError=result.stderr)
            else:
                return CompileResponse(hasError=False, compilerError=None)

        except subprocess.SubprocessError as e:
            raise HTTPException(status_code=500, detail=f"Compilation process failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)