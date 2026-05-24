import aiohttp
from aiohttp import web
import json
import re
from sympy import sympify, SympifyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a more restrictive regex pattern for basic arithmetic expressions
SAFE_EXPRESSION_REGEX = r'^[\d\s\+\-\*/\(\)]+$'

async def calculate_expression(request):
    try:
        # Validate content type
        if request.content_type != 'application/json':
            return web.json_response({'error': 'Invalid content type'}, status=400)

        # Parse request body
        data = await request.json()

        # Validate input
        if 'expression' not in data or not isinstance(data['expression'], str):
            return web.json_response({'error': 'Invalid input'}, status=400)

        expression = data['expression'].strip()

        # Validate and sanitize the expression
        if not re.match(SAFE_EXPRESSION_REGEX, expression):
            return web.json_response({'error': 'Invalid input'}, status=400)

        # Check input length
        if len(expression) > 500:  # Reduced limit to prevent resource exhaustion
            return web.json_response({'error': 'Input too long'}, status=400)

        # Calculate the result using sympy
        try:
            result = sympify(expression, evaluate=True)
        except (SympifyError, ZeroDivisionError) as e:
            logging.error(f"Error evaluating expression: {e}")
            return web.json_response({'error': 'Invalid input'}, status=400)

        return web.json_response({'result': str(result)}, status=200)

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)

# Create the web application
app = web.Application()

# Add security headers middleware
@web.middleware
async def security_headers_middleware(request, handler):
    response = await handler(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'none';"
    return response

app.middlewares.append(security_headers_middleware)

# Add routes
app.router.add_post('/calculator', calculate_expression)

if __name__ == '__main__':
    # Run the web application
    web.run_app(app, host='0.0.0.0', port=5000)