from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import subprocess
import re
from typing import List, Optional

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: Optional[constr(regex=r'^[\s-]*$')] = None  # Allow only safe characters (spaces and hyphens)
    command_regex: constr(regex=r'^[\w\s.*]+$')  # Allow only safe regex characters

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=List[ProcessInfo])
async def monitor_commands(request: MonitorRequest):
    try:
        # Prepare the command to execute
        command = ["ps"] + (request.filter_flags.split() if request.filter_flags else []) + ["-eo", "pid,command"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Filter the output based on the regex
        process_list = []
        for line in result.stdout.splitlines()[1:]:  # Skip the header line
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            pid = int(parts[0])
            command_string = parts[1]
            if re.search(request.command_regex, command_string):
                process_list.append(ProcessInfo(processId=pid, processString=command_string))
        
        return process_list

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing command")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)