from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import os

# Initialize FastAPI app
app = FastAPI(
    title="LoggingAPI",
    description="A simple webapp API for logging functionality.",
    version="1.0.11"
)

# Define the log file path
LOG_FILE = "logs.txt"

# Ensure the log file exists and is in a safe directory
SAFE_DIRECTORY = os.getcwd()
LOG_FILE_PATH = os.path.join(SAFE_DIRECTORY, LOG_FILE)

if not os.path.commonpath([os.path.abspath(LOG_FILE_PATH), SAFE_DIRECTORY]) == SAFE_DIRECTORY:
    raise Exception("Log file path is not within the safe directory.")

# Create the log file if it doesn't exist
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w") as f:
        pass  # Create an empty file

# Pydantic model for the log message
class LogMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="The log message to be stored.")

@app.post("/log", summary="Log a message", description="Log a message to the server.")
async def log_message(log: LogMessage):
    """
    Endpoint to log a message to the server.
    """
    try:
        # Sanitize and validate the message
        sanitized_message = log.message.strip()
        if not sanitized_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty or whitespace.")

        # Write the sanitized message to the log file
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(sanitized_message + "\n")

        return {"detail": "Log message successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while logging the message.") from e

@app.get("/logs", summary="Retrieve logs", description="Retrieve all logged messages.")
async def retrieve_logs():
    """
    Endpoint to retrieve all logged messages.
    """
    try:
        # Read the log file
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            logs = f.read()

        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the logs.") from e

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)