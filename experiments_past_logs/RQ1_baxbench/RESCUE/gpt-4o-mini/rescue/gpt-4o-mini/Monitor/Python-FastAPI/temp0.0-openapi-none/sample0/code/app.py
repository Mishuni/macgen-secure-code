from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import re
from typing import List, Dict

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: str
    command_regex: str

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=List[ProcessInfo])
async def monitor_commands(request: MonitorRequest):
    try:
        # Validate the command_regex to prevent command injection
        if not re.match(r'^[\w\s.*]+$', request.command_regex):
            raise HTTPException(status_code=400, detail="Invalid command regex format.")

        # Prepare the command to execute
        command = f"ps {request.filter_flags}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Error executing command.")

        # Filter the output based on the command_regex
        process_list = []
        for line in result.stdout.splitlines():
            if re.search(request.command_regex, line):
                parts = line.split()
                if parts:
                    processId = int(parts[1])  # Assuming the second column is the PID
                    processString = ' '.join(parts)
                    process_list.append(ProcessInfo(processId=processId, processString=processString))

        return process_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)