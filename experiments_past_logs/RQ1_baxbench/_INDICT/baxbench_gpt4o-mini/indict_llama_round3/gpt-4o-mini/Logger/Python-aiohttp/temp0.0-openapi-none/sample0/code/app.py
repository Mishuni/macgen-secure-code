from aiohttp import web
import json
import aiofiles

LOG_FILE = 'logs.txt'

async def log_message(request):
    try:
        data = await request.json()
        message = data.get('message')
        
        if not isinstance(message, str) or not message.strip():
            return web.json_response({'error': 'Invalid message'}, status=400)

        async with aiofiles.open(LOG_FILE, 'a') as f:
            await f.write(message.strip() + '\n')

        return web.json_response({'status': 'Log message successful'}, status=200)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def retrieve_logs(request):
    try:
        async with aiofiles.open(LOG_FILE, 'r') as f:
            logs = await f.read()
        
        return web.Response(text=logs, content_type='text/plain', status=200)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)