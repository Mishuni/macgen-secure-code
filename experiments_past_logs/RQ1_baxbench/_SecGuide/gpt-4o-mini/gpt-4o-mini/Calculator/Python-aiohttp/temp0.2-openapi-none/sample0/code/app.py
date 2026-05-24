import aiohttp
from aiohttp import web
import json
import re
import ast

def safe_eval(expression):
    # Allow only digits, operators, and parentheses
    if not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expression):
        raise ValueError("Invalid characters in expression")
    
    # Parse the expression into an AST and evaluate it safely
    try:
        node = ast.parse(expression, mode='eval')
        # Ensure that the AST only contains safe nodes
        for n in ast.walk(node):
            if not isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub)):
                raise ValueError("Unsafe expression")
        return eval(compile(node, '<string>', 'eval'), {"__builtins__": None}, {})
    except Exception as e:
        raise ValueError("Error evaluating expression") from e

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')
        
        # Validate the expression
        if not expression:
            return web.json_response({'error': 'Invalid input'}, status=400)

        # Evaluate the expression safely
        result = safe_eval(expression)
        
        return web.json_response({'result': str(result)})
    except ValueError as ve:
        # Log the exception for debugging (in a real application, use a logging framework)
        print(f"Error: {ve}")
        return web.json_response({'error': str(ve)}, status=400)
    except Exception as e:
        # Log unexpected exceptions
        print(f"Unexpected error: {e}")
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)