from aiohttp import web
import json
import os
import html

# Define the file name for storing logs
LOG_FILE = "logs.txt"

# Ensure the log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        pass

async def log_message(request):
    try:
        data = await request.json()
        message = html.escape(data.get('message', ''))
        
        if not message or len(message) > 1000:  # Example length validation
            return web.Response(status=400, text="Invalid log message")
        
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(message + '\n')
        except OSError:
            return web.Response(status=500, text="Error writing log")
        
        return web.Response(status=200, text="Log message successful")
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

async def retrieve_logs(request):
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.read()
        return web.Response(status=200, text=logs, content_type='text/plain')
    except Exception:
        return web.Response(status=500, text="Error reading logs")

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)