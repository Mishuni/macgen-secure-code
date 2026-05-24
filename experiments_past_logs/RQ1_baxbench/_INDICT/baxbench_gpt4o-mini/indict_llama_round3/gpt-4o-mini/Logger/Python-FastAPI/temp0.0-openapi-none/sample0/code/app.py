from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os

app = FastAPI()

LOG_FILE = "logs.txt"

class LogMessage(BaseModel):
    message: constr(strip_whitespace=True, min_length=1)

@app.post("/log")
async def log_message(log: LogMessage):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log.message + "\n")
        return {"message": "Log message successful"}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to log message")

@app.get("/logs")
async def retrieve_logs():
    if not os.path.exists(LOG_FILE):
        return {"logs": []}
    
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
        return {"logs": [log.strip() for log in logs]}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)