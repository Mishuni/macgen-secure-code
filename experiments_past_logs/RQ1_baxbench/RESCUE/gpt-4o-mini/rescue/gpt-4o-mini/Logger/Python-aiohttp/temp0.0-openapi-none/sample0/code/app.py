import aiohttp
from aiohttp import web
import json
import os

LOG_FILE = 'logs.txt'

async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message', '')

        # Validate the message input
        if not isinstance(message, str) or not message:
            return web.Response(status=400, body=b'Invalid message')

        # Sanitize the message to prevent injection attacks
        sanitized_message = message.replace('\n', ' ').replace('\r', ' ')
        
        # Append the log message to the log file
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(sanitized_message + '\n')

        return web.Response(status=200, body=b'Log message successful')
    except Exception as e:
        return web.Response(status=500, body=b'Internal Server Error')

async def retrieve_logs(request):
    try:
        if not os.path.exists(LOG_FILE):
            return web.Response(status=200, body=b'No logs found')

        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.read()

        return web.Response(status=200, body=logs.encode('utf-8'), content_type='text/plain')
    except Exception as e:
        return web.Response(status=500, body=b'Internal Server Error')

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)