import aiohttp
from aiohttp import web
import json
import re

async def calculator_handler(request):
    # Validate content-type
    if request.headers.get('Content-Type') != 'application/json':
        return web.Response(status=400, text='Invalid Content-Type')

    # Parse JSON request body
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')

    # Validate expression format
    expression = data.get('expression')
    if not isinstance(expression, str) or not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expression):
        return web.Response(status=400, text='Invalid input')

    # Evaluate the expression safely
    try:
        result = eval(expression, {"__builtins__": None}, {})
    except Exception:
        return web.Response(status=400, text='Error evaluating expression')

    # Prepare and return the response
    return web.json_response({'result': str(result)})

async def init_app():
    app = web.Application()
    app.router.add_post('/calculator', calculator_handler)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=5000)