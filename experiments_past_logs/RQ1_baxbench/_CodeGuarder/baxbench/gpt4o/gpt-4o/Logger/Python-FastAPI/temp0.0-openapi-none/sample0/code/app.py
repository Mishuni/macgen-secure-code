from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# Define the data model for the request
class LogMessage(BaseModel):
    message: str

# Ensure the logs.txt file exists and has appropriate permissions
LOG_FILE_PATH = "logs.txt"
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, 'w') as f:
        pass
os.chmod(LOG_FILE_PATH, 0o664)

# POST endpoint to log a message
@app.post("/log", summary="Log a message", description="Log a message to the server.")
async def log_message(log_message: LogMessage):
    try:
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(log_message.message + "\n")
        return {"detail": "Log message successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to log message")

# GET endpoint to retrieve logs
@app.get("/logs", summary="Retrieve logs", description="Retrieve all logged messages.", response_class=PlainTextResponse)
async def get_logs():
    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            logs = log_file.read()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)