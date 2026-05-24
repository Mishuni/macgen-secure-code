import aiohttp
from aiohttp import web
import json
import os
import re
import stat

LOG_FILE = 'logs.txt'

# Function to sanitize log messages
def sanitize_message(message):
    # Remove control characters and limit the length of the message
    return re.sub(r'[\x00-\x1F\x7F]', '', message)[:1024]

async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message', '')

        # Validate the message to ensure it is a string
        if not isinstance(message, str):
            return web.Response(status=400, text='Invalid message format.')

        # Sanitize the message
        sanitized_message = sanitize_message(message)

        # Log the message to the file with proper permissions
        with open(LOG_FILE, 'a') as f:
            f.write(sanitized_message + '\n')

        return web.Response(status=200, text='Log message successful')
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON format.')
    except Exception as e:
        return web.Response(status=500, text='Internal server error.')

async def retrieve_logs(request):
    if not os.path.exists(LOG_FILE):
        return web.Response(status=200, text='No logs available.')

    with open(LOG_FILE, 'r') as f:
        logs = f.read()

    return web.Response(status=200, text=logs, content_type='text/plain')

# Set appropriate file permissions for the log file
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        pass
    os.chmod(LOG_FILE, stat.S_IRUSR | stat.S_IWUSR)  # rw-------

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)