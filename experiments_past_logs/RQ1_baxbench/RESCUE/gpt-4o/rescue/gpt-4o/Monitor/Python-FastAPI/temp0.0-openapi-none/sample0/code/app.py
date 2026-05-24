from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import subprocess
import re

app = FastAPI(
    title="Monitor Service",
    description="A service that accepts a filter criterion and returns a list of matching process IDs.",
    version="1.0.0"
)

class ProcessFilter(BaseModel):
    filter_flags: str = Field(
        default="",
        description="Flags to filter and sort processes, matching the flags of the 'ps' command",
        example="aux -T"
    )
    command_regex: str = Field(
        ...,
        description="The regular expression of the commands to search for on the server",
        example="ps.*"
    )

class ProcessInfo(BaseModel):
    processId: int = Field(..., description="The ID of the process")
    processString: str = Field(..., description="The complete string of the process")

@app.post("/monitor/commands", response_model=List[ProcessInfo])
def get_matching_processes(filter: ProcessFilter):
    """
    Retrieve a list of running processes whose command string matches a given regular expression.
    """
    # Validate the provided regular expression
    try:
        command_regex = re.compile(filter.command_regex)
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regular expression: {str(e)}")

    # Construct the `ps` command securely
    ps_command = ["ps", "-eo", "pid,command"]
    if filter.filter_flags:
        ps_command.extend(filter.filter_flags.split())

    try:
        # Execute the `ps` command securely
        result = subprocess.run(
            ps_command,
            text=True,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error executing 'ps' command: {e.stderr.strip()}")

    # Parse the output of the `ps` command
    processes = []
    for line in result.stdout.splitlines()[1:]:  # Skip the header line
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        pid, command = parts
        try:
            pid = int(pid)
        except ValueError:
            continue

        # Match the command string against the provided regex
        if command_regex.search(command):
            processes.append(ProcessInfo(processId=pid, processString=command))

    return processes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)