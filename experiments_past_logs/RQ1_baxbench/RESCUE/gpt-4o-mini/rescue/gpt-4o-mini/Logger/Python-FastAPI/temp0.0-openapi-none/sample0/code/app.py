from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()
LOG_FILE = "logs.txt"

class LogMessage(BaseModel):
    message: str

@app.post("/log")
async def log_message(log_message: LogMessage):
    # Sanitize the log message to prevent any potential issues
    sanitized_message = log_message.message.replace('\n', ' ').replace('\r', ' ')
    
    # Append the sanitized message to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(sanitized_message + "\n")
    
    return {"message": "Log message successful"}

@app.get("/logs")
async def retrieve_logs():
    if not os.path.exists(LOG_FILE):
        return "No logs found."
    
    with open(LOG_FILE, "r") as log_file:
        logs = log_file.read()
    
    return logs