from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import subprocess
import os
import tempfile
import shutil
import re

app = FastAPI()

class CompileRequest(BaseModel):
    fileName: constr(regex=r'^[\w\-\.]+$')  # Only allow alphanumeric, hyphens, underscores, and dots
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str = None

def is_valid_code(content: str) -> bool:
    # Implement basic checks for valid code content
    # This is a placeholder for more sophisticated validation
    return bool(re.match(r'^[\s\S]*$', content) and len(content) < 10000)  # Example: limit content length

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Validate file content
    if not is_valid_code(request.fileContent):
        raise HTTPException(status_code=400, detail="Invalid code content.")

    # Determine the file extension
    file_extension = request.fileName.split('.')[-1]

    # Create a secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, request.fileName)
        
        # Write the content to the temporary file
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(request.fileContent)

        try:
            if file_extension == "cpp":
                # Compile C++ code
                compile_command = ["g++", temp_file_path, "-o", os.path.join(temp_dir, "output")]
                result = subprocess.run(compile_command, capture_output=True, text=True)
                if result.returncode != 0:
                    return CompileResponse(hasError=True, compilerError=result.stderr.strip())
                return CompileResponse(hasError=False)

            elif file_extension == "ts":
                # Compile TypeScript code
                compile_command = ["tsc", temp_file_path]
                result = subprocess.run(compile_command, capture_output=True, text=True)
                if result.returncode != 0:
                    return CompileResponse(hasError=True, compilerError=result.stderr.strip())
                return CompileResponse(hasError=False)

            else:
                raise HTTPException(status_code=400, detail="Unsupported file type. Only .cpp and .ts files are allowed.")

        except Exception as e:
            raise HTTPException(status_code=500, detail="An error occurred during compilation.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)