from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import re

app = FastAPI(
    title="Monitor Service",
    description="A service that accepts a filter criterion and returns a list of matching process IDs.",
    version="1.0.0"
)

class MonitorRequest(BaseModel):
    filter_flags: str = "aux"
    command_regex: str

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=list[ProcessInfo])
async def get_running_processes(request: MonitorRequest):
    try:
        # Validate filter_flags to ensure it only contains safe characters
        if not re.match(r'^[a-zA-Z\s\-]*$', request.filter_flags):
            raise HTTPException(status_code=400, detail="Invalid filter flags provided.")

        # Execute the ps command with the provided flags
        ps_command = ["ps"] + request.filter_flags.split()
        result = subprocess.run(ps_command, capture_output=True, text=True, check=True)
        
        # Filter the processes based on the command_regex
        matching_processes = []
        for line in result.stdout.splitlines():
            if re.search(request.command_regex, line):
                parts = line.split(None, 3)  # Split into parts, assuming the 4th part is the command
                if len(parts) >= 2:
                    try:
                        process_id = int(parts[1])
                        process_string = line
                        matching_processes.append(ProcessInfo(processId=process_id, processString=process_string))
                    except ValueError:
                        continue

        return matching_processes

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error executing ps command: {e}")

    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regular expression: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)