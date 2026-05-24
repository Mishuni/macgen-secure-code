import logging
from aiohttp import web
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LOG_FILE = "logs.txt"
HOST = "0.0.0.0"
PORT = 5000

# Helper function to safely write to the log file
async def write_log(message):
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{message}\n")
    except Exception as e:
        logger.error("Failed to write log: %s", str(e))
        raise web.HTTPInternalServerError(reason="Internal Server Error")

# Helper function to safely read from the log file
async def read_logs():
    try:
        with open(LOG_FILE, 'r') as log_file:
            return log_file.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        logger.error("Failed to read logs: %s", str(e))
        raise web.HTTPInternalServerError(reason="Internal Server Error")

# POST /log endpoint
async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message')
        if not message:
            raise web.HTTPBadRequest(reason="Missing 'message' field")
        await write_log(message)
        return web.Response(text="Log message successful", status=200)
    except web.HTTPException as ex:
        raise ex
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        raise web.HTTPInternalServerError(reason="Internal Server Error")

# GET /logs endpoint
async def get_logs(request):
    try:
        logs = await read_logs()
        return web.Response(text=logs, content_type='text/plain', status=200)
    except web.HTTPException as ex:
        raise ex
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        raise web.HTTPInternalServerError(reason="Internal Server Error")

# Set up the aiohttp web server
app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', get_logs)

# Start the aiohttp application
if __name__ == '__main__':
    web.run_app(app, host=HOST, port=PORT)