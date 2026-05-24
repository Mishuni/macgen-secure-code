import aiohttp
from aiohttp import web
import json

def safe_eval(expression):
    # A simple parser for basic arithmetic expressions
    try:
        # Only allow numbers and basic operators
        allowed_chars = "0123456789+-*/(). "
        if any(char not in allowed_chars for char in expression):
            raise ValueError("Invalid characters in expression")
        
        # Evaluate the expression safely using eval with limited scope
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception:
        raise ValueError("Invalid expression")

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')
        
        # Validate the expression
        if not isinstance(expression, str) or not expression.strip():
            return web.Response(status=400, text='Invalid input')
        
        result = safe_eval(expression)
        return web.json_response({'result': str(result)})
    except ValueError:
        return web.Response(status=400, text='Invalid input')

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)