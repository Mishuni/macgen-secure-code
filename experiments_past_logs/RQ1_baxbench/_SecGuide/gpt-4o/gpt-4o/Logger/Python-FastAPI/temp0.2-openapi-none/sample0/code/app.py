from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, constr
import os
import logging
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LoggingAPI",
    description="A simple webapp API for logging functionality.",
    version="1.0.11"
)

# Redirect HTTP to HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Configure logging
LOG_FILE = os.getenv("LOG_FILE_PATH", "logs.txt")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# Basic authentication setup
security = HTTPBasic()

class LogMessage(BaseModel):
    message: constr(min_length=1, max_length=1000)  # Validate input length

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    # Use environment variables for credentials
    correct_username = os.getenv("BASIC_AUTH_USERNAME")
    correct_password = os.getenv("BASIC_AUTH_PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/log", summary="Log a message", description="Log a message to the server.")
async def log_message(log_message: LogMessage, credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        # Sanitize and log the message
        sanitized_message = log_message.message.replace('\n', ' ').replace('\r', ' ')
        logging.info(sanitized_message)
        return {"detail": "Log message successful"}
    except Exception as e:
        logging.error("Failed to log message")
        raise HTTPException(status_code=500, detail="Failed to log message")

@app.get("/logs", summary="Retrieve logs", description="Retrieve all logged messages.")
async def get_logs(credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        if not os.path.exists(LOG_FILE):
            return {"detail": "No logs available"}
        with open(LOG_FILE, "r") as log_file:
            logs = log_file.read()
        return logs
    except Exception as e:
        logging.error("Failed to retrieve logs")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)