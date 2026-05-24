from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import shlex

app = FastAPI()

class CompileRequest(BaseModel):
    fileName: str
    fileContent: str

class CompileResponse(BaseModel):
    hasError: bool
    compilerError: str | None

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    # Create a temporary file to hold the code
    with open(request.fileName, 'w') as code_file:
        code_file.write(request.fileContent)

    # Determine the file extension to choose the appropriate compiler
    if request.fileName.endswith('.cpp'):
        command = ['g++', request.fileName, '-o', 'output']
    elif request.fileName.endswith('.ts'):
        command = ['tsc', request.fileName]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Execute the compilation command
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            return CompileResponse(hasError=True, compilerError=result.stderr.decode())
        return CompileResponse(hasError=False, compilerError=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)