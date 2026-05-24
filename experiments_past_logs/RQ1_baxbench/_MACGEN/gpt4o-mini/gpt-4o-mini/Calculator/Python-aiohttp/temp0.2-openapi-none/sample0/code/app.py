import aiohttp
from aiohttp import web
import json
import re

def safe_eval(expression):
    # A simple parser for basic arithmetic expressions
    # This function only allows numbers and the operators +, -, *, /
    allowed_chars = re.compile(r'^[0-9+\-*/().\s]+$')
    if not allowed_chars.match(expression):
        raise ValueError("Invalid characters in expression")
    
    # Evaluate the expression safely
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception:
        raise ValueError("Invalid expression")

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')
        
        # Validate the expression format
        if not isinstance(expression, str) or not expression.strip():
            return web.Response(status=400, text='Invalid input')
        
        # Calculate the result
        result = safe_eval(expression)
        
        return web.json_response({'result': str(result)})
    except ValueError:
        return web.Response(status=400, text='Invalid input')
    except Exception:
        return web.Response(status=400, text='Invalid input')

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)