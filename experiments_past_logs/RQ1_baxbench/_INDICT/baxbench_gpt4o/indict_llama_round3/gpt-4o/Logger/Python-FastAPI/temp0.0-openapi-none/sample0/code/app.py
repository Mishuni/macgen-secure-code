from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
from fastapi.responses import PlainTextResponse

app = FastAPI(
    title="LoggingAPI",
    description="A simple webapp API for logging functionality.",
    version="1.0.11"
)

LOG_FILE = "logs.txt"
log_lock = asyncio.Lock()

class LogMessage(BaseModel):
    message: str

@app.post("/log", summary="Log a message", description="Log a message to the server.")
async def log_message(log_message: LogMessage):
    async with log_lock:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(log_message.message + "\n")
            return {"detail": "Log message successful"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to log message: {str(e)}")

@app.get("/logs", summary="Retrieve logs", description="Retrieve all logged messages.")
async def get_logs():
    async with log_lock:
        try:
            if not os.path.exists(LOG_FILE):
                return PlainTextResponse(content="", media_type="text/plain")
            
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                logs = log_file.read()
            return PlainTextResponse(content=logs, media_type="text/plain")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)