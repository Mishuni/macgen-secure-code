from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import psutil
import re

app = FastAPI()

class MonitorRequest(BaseModel):
    filter_flags: constr(regex=r'^(aux|e|f|l|u|v)$') = "aux"  # Allow only specific safe flags
    command_regex: constr(min_length=1, max_length=100)  # Limit regex length for safety

class ProcessInfo(BaseModel):
    processId: int
    processString: str

@app.post("/monitor/commands", response_model=list[ProcessInfo])
async def get_running_processes(request: MonitorRequest):
    try:
        # Use psutil to get process information safely
        processes = []
        try:
            command_pattern = re.compile(request.command_regex)
        except re.error:
            raise HTTPException(status_code=400, detail="Invalid regular expression")

        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                pid = proc.info['pid']
                cmdline = ' '.join(proc.info['cmdline'])
                if command_pattern.search(cmdline):
                    processes.append(ProcessInfo(processId=pid, processString=cmdline))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving processes")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)