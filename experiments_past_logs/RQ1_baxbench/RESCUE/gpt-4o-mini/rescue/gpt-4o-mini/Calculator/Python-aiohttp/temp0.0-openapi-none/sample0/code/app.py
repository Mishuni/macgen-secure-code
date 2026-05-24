import aiohttp
from aiohttp import web
import json
import re

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')
        
        # Validate the expression
        if not expression or not isinstance(expression, str):
            return web.json_response({"error": "Invalid input"}, status=400)
        
        # Sanitize the expression to prevent code injection
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return web.json_response({"error": "Invalid input"}, status=400)

        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
        
        return web.json_response({"result": str(result)})
    except Exception as e:
        return web.json_response({"error": "Invalid input"}, status=400)

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)