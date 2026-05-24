from aiohttp import web
import json

LOG_FILE = "logs.txt"

def escape(message):
    # Simple escape function to prevent log injection
    return message.replace("\n", "\\n").replace("\r", "\\r")

async def log_message(request):
    try:
        data = await request.json()
        message = data.get("message")
        
        if not message or not isinstance(message, str):
            return web.json_response({"error": "Invalid message"}, status=400)

        # Sanitize the message
        message = escape(message)

        # Redact sensitive information
        if "sensitive" in message:
            message = "REDACTED"

        with open(LOG_FILE, "a") as f:
            f.write(message + "\n")
        
        return web.json_response({"status": "Log message successful"}, status=200)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def retrieve_logs(request):
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.read()
        
        return web.Response(text=logs, content_type='text/plain', status=200)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app = web.Application()
app.router.add_post('/log', log_message)
app.router.add_get('/logs', retrieve_logs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)