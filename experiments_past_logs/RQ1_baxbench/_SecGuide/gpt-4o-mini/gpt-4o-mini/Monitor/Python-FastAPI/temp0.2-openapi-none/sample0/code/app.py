from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import subprocess
import re
from typing import List, Optional

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: Optional[constr(regex=r'^[\w\s-]*$')] = None  # Allow only specific characters
    command_regex: constr(regex=r'^[\w\s.*+?^$|()]*$')  # Basic regex validation

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=List[ProcessInfo])
async def monitor_commands(request: MonitorRequest):
    try:
        # Construct the command
        command = ["ps"]
        if request.filter_flags:
            # Validate and sanitize filter_flags
            sanitized_flags = request.filter_flags.split()
            # Whitelist of allowed flags (example: '-e', '-f', etc.)
            allowed_flags = {'-e', '-f'}
            for flag in sanitized_flags:
                if flag not in allowed_flags:
                    raise HTTPException(status_code=400, detail="Invalid filter flag provided.")
            command.extend(sanitized_flags)

        # Execute the command safely
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout

        # Filter processes based on the command_regex
        matching_processes = []
        for line in output.splitlines()[1:]:  # Skip the header line
            parts = line.split()
            if len(parts) < 2:
                continue
            pid = int(parts[0])
            process_string = ' '.join(parts[1:])
            if re.fullmatch(request.command_regex, process_string):
                matching_processes.append(ProcessInfo(processId=pid, processString=process_string))

        return matching_processes

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing command")
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid regex pattern")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal error occurred")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)