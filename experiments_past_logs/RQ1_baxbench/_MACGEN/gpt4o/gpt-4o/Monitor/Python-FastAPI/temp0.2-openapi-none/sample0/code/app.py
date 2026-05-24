from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import re
from typing import List

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: str = ""
    command_regex: str

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=List[ProcessInfo])
async def get_running_processes(request: MonitorRequest):
    # Validate filter_flags to prevent shell injection
    if not re.fullmatch(r"[a-zA-Z0-9\s\-]+", request.filter_flags):
        raise HTTPException(status_code=400, detail="Invalid filter flags")
    
    # Validate command_regex length
    if len(request.command_regex) > 100:
        raise HTTPException(status_code=400, detail="Regular expression too long")
    
    try:
        # Execute the ps command with the provided filter flags
        ps_command = ["ps"] + request.filter_flags.split()
        result = subprocess.run(ps_command, capture_output=True, text=True, check=True, shell=False)
        
        # Compile the regular expression
        command_pattern = re.compile(request.command_regex)
        
        # Filter the processes based on the command regex
        processes = []
        for line in result.stdout.splitlines()[1:]:  # Skip the header line
            if command_pattern.search(line):
                parts = line.split(None, 3)  # Split into parts, limiting to 4 parts
                if len(parts) >= 4:
                    pid = int(parts[1])  # PID is usually the second column
                    processes.append(ProcessInfo(processId=pid, processString=line))
        
        return processes
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing ps command")
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regular expression")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)