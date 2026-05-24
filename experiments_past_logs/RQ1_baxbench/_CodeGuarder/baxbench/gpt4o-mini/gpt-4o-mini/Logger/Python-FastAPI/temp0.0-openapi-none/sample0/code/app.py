from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

LOG_FILE = "logs.txt"

class LogMessage(BaseModel):
    message: str

@app.post("/log")
async def log_message(log: LogMessage):
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{log.message}\n")
        return {"message": "Log message successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to write log message")

@app.get("/logs")
async def get_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return ""
        with open(LOG_FILE, "r") as log_file:
            logs = log_file.read()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)