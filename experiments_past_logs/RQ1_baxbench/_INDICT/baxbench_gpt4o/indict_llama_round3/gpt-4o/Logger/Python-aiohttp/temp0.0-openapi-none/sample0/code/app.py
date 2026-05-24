import aiohttp
from aiohttp import web
import os
import asyncio

# Define the file where logs will be stored
LOG_FILE = "logs.txt"

# Ensure the log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        pass

# Lock for handling concurrent file access
file_lock = asyncio.Lock()

async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message', '').strip()
        
        if not message:
            return web.Response(text="Invalid log message", status=400)
        
        # Sanitize the message to prevent log injection
        sanitized_message = message.replace('\n', ' ').replace('\r', ' ')
        
        async with file_lock:
            with open(LOG_FILE, 'a') as f:
                f.write(sanitized_message + '\n')
        
        return web.Response(text="Log message successful", status=200)
    except aiohttp.web_exceptions.HTTPBadRequest:
        return web.Response(text="Invalid JSON format", status=400)
    except Exception as e:
        return web.Response(text=f"Error: {str(e)}", status=500)

async def retrieve_logs(request):
    try:
        async with file_lock:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
        
        return web.Response(text=logs, status=200, content_type='text/plain')
    except Exception as e:
        return web.Response(text=f"Error: {str(e)}", status=500)

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)