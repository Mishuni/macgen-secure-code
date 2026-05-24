import os
import aiohttp
from aiohttp import web
import asyncio

# Define constants
LOG_FILE = "logs.txt"
STORAGE_DIR = os.path.abspath(os.getcwd())

# Ensure the log file is in a safe directory
LOG_FILE_PATH = os.path.abspath(os.path.join(STORAGE_DIR, LOG_FILE))
if not LOG_FILE_PATH.startswith(STORAGE_DIR):
    raise ValueError("Log file path is not within the safe directory.")

# Create the log file if it doesn't exist
if not os.path.isfile(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w") as f:
        pass

# Helper function to sanitize and validate input
def sanitize_message(message):
    if not isinstance(message, str):
        raise ValueError("Message must be a string.")
    if len(message.strip()) == 0:
        raise ValueError("Message cannot be empty.")
    return message.strip()

# POST /log - Log a message
async def log_message(request):
    try:
        # Parse JSON body
        data = await request.json()
        message = data.get("message")
        if message is None:
            return web.Response(status=400, text="Missing 'message' field in request body.")
        
        # Sanitize and validate the message
        sanitized_message = sanitize_message(message)

        # Write the message to the log file
        async with aiofiles.open(LOG_FILE_PATH, mode="a") as log_file:
            await log_file.write(sanitized_message + "\n")

        return web.Response(status=200, text="Log message successful.")
    except ValueError as e:
        return web.Response(status=400, text=str(e))
    except Exception as e:
        return web.Response(status=500, text="Internal Server Error.")

# GET /logs - Retrieve all logs
async def get_logs(request):
    try:
        # Read the log file
        async with aiofiles.open(LOG_FILE_PATH, mode="r") as log_file:
            logs = await log_file.read()

        return web.Response(status=200, text=logs, content_type="text/plain")
    except Exception as e:
        return web.Response(status=500, text="Internal Server Error.")

# Create the aiohttp application
app = web.Application()
app.router.add_post("/log", log_message)
app.router.add_get("/logs", get_logs)

# Run the application
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)