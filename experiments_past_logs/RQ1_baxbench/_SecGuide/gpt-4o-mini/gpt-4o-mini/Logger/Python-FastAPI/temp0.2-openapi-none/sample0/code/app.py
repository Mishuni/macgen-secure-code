from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, constr
import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse

app = FastAPI()

LOG_FILE = os.getenv("LOG_FILE", "logs.txt")  # Use environment variable for log file path

# Configure logging
logger = logging.getLogger("LogMessages")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)  # 10 MB limit
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class LogMessage(BaseModel):
    message: constr(min_length=1)  # Ensure message is not empty

@app.post("/log")
async def log_message(log: LogMessage):
    # Sanitize input to prevent log injection
    sanitized_message = log.message.replace('\n', ' ').replace('\r', ' ')
    
    # Additional sanitization could be added here
    logger.info(sanitized_message)
    
    return {"detail": "Log message successful"}

@app.get("/logs")
async def retrieve_logs():
    if not os.path.exists(LOG_FILE):
        return JSONResponse(content={"detail": "Log file not found"}, status_code=404)
    
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.read()
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)