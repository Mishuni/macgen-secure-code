from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List
import subprocess
import re

app = FastAPI()

class ProcessFilterRequest(BaseModel):
    filter_flags: str = Field(default="", description="Flags to filter and sort processes, matching the flags of the 'ps' command")
    command_regex: str = Field(..., description="The regular expression of the commands to search for on the server")

class ProcessResponse(BaseModel):
    processId: int
    processString: str

class ErrorResponse(BaseModel):
    code: int
    message: str

@app.post("/monitor/commands", response_model=List[ProcessResponse], responses={400: {"model": ErrorResponse}})
async def monitor_commands(request: Request, filter_request: ProcessFilterRequest):
    # Validate content-type
    if request.headers.get('content-type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid content-type")

    # Validate command_regex
    try:
        re.compile(filter_request.command_regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regular expression")

    # Execute the ps command
    try:
        result = subprocess.run(
            ['ps', filter_request.filter_flags],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="Error executing ps command")

    # Filter processes based on the command_regex
    processes = []
    for line in result.stdout.splitlines():
        match = re.search(filter_request.command_regex, line)
        if match:
            parts = line.split(None, 3)
            if len(parts) >= 4:
                try:
                    process_id = int(parts[0])
                    process_string = parts[3]
                    processes.append(ProcessResponse(processId=process_id, processString=process_string))
                except ValueError:
                    continue

    return processes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)