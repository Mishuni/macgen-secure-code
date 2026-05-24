import aiohttp
from aiohttp import web
import aiofiles
import asyncio
import json
import logging
import os

# File to store logs
LOG_FILE = "logs.txt"

# Configure logging for errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure log file has appropriate permissions
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        os.chmod(LOG_FILE, 0o600)  # Read/write for owner only

# Function to log a message to the file
async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message', '').strip()

        # Validate message
        if not message or len(message) > 1024:
            return web.Response(text="Invalid message", status=400)

        # Sanitize message to prevent log injection
        sanitized_message = message.replace('\n', ' ').replace('\r', ' ')

        # Write the message to the log file
        async with aiofiles.open(LOG_FILE, mode='a') as f:
            await f.write(sanitized_message + '\n')

        return web.Response(text="Log message successful", status=200)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        return web.Response(text="Invalid JSON", status=400)
    except Exception as e:
        logger.error("Unexpected error")
        return web.Response(text="Internal server error", status=500)

# Function to retrieve all logs
async def get_logs(request):
    try:
        async with aiofiles.open(LOG_FILE, mode='r') as f:
            logs = await f.read()
        return web.Response(text=logs, content_type='text/plain', status=200)
    except FileNotFoundError:
        return web.Response(text="No logs found", status=200)
    except Exception as e:
        logger.error("Unexpected error")
        return web.Response(text="Internal server error", status=500)

# Create the application and add routes
app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', get_logs)

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)