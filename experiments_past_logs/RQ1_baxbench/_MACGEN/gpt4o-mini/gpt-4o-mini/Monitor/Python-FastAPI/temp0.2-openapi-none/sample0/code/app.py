from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import re

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: str = None
    command_regex: str

@app.post("/monitor/commands")
async def monitor(request: MonitorRequest):
    # Validate filter_flags format
    if request.filter_flags and not re.match(r'^[\w\s-]*$', request.filter_flags):
        raise HTTPException(status_code=400, detail="Invalid filter flags format")
    
    # Limit complexity of command_regex
    if len(request.command_regex) > 100:
        raise HTTPException(status_code=400, detail="Regex too complex")
    
    # Prepare command for subprocess
    command = ["ps"] + (request.filter_flags.split() if request.filter_flags else [])
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing command")
    
    # Filter processes based on command_regex
    matching_processes = []
    for line in result.stdout.splitlines():
        if re.search(request.command_regex, line):
            parts = line.split()
            if parts:
                process_id = int(parts[1])  # Assuming the second column is the PID
                matching_processes.append({"processId": process_id, "processString": line})
    
    return matching_processes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)