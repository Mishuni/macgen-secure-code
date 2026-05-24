from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import re
from typing import List, Dict

app = FastAPI()

class CommandRequest(BaseModel):
    filter_flags: str
    command_regex: str

class ProcessResponse(BaseModel):
    processId: int
    processString: str

class ErrorResponse(BaseModel):
    code: int
    message: str

@app.post("/monitor/commands", response_model=List[ProcessResponse], responses={400: {"model": ErrorResponse}})
async def monitor_commands(request: CommandRequest):
    try:
        # Validate the command_regex
        re.compile(request.command_regex)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regular expression for command_regex")

    # Execute the ps command with the provided filter_flags
    try:
        result = subprocess.run(['ps'] + request.filter_flags.split(), capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Error executing ps command: {e}")

    # Filter the output based on the command_regex
    matching_processes = []
    for line in output.splitlines()[1:]:  # Skip the header line
        parts = line.split(None, 3)  # Split into parts, limit to 4 to get PID and command
        if len(parts) < 4:
            continue
        pid = int(parts[0])
        command_string = parts[3]
        if re.search(request.command_regex, command_string):
            matching_processes.append(ProcessResponse(processId=pid, processString=command_string))

    return matching_processes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)