from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os

app = FastAPI()

LOG_FILE = "logs.txt"

class LogMessage(BaseModel):
    message: constr(max_length=256)  # Limit log message length to 256 characters

@app.post("/log")
async def log_message(log: LogMessage):
    sanitized_message = log.message.replace("\n", "\\n").replace("\r", "\\r")  # Sanitize log message
    try:
        with open(LOG_FILE, "a") as f:
            f.write(sanitized_message + "\n")
        return {"message": "Log message successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to log message")

@app.get("/logs")
async def retrieve_logs():
    if not os.path.exists(LOG_FILE):
        return ""
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.read()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)