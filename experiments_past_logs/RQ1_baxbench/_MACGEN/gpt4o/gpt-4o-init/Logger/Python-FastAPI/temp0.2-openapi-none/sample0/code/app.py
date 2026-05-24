from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(
    title="LoggingAPI",
    description="A simple webapp API for logging functionality.",
    version="1.0.11"
)

LOG_FILE = "logs.txt"

class LogMessage(BaseModel):
    message: str

@app.post("/log", summary="Log a message", description="Log a message to the server.")
async def log_message(log: LogMessage):
    if len(log.message) > 1000:
        raise HTTPException(status_code=400, detail="Log message too long")
    
    safe_message = log.message.replace("\n", "\\n").replace("\r", "\\r")
    
    try:
        with open(LOG_FILE, "a") as file:
            file.write(safe_message + "\n")
        return {"detail": "Log message successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to log message")

@app.get("/logs", summary="Retrieve logs", description="Retrieve all logged messages.")
async def get_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return ""
        with open(LOG_FILE, "r") as file:
            logs = file.read()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)