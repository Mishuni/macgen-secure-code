from aiohttp import web
import json

async def calculate_expression(request):
    # Parse and validate the request body
    if request.headers.get('content-type') != 'application/json':
        return web.json_response({'error': 'Invalid content-type'}, status=400)

    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)

    expression = data.get('expression')
    if not expression or not isinstance(expression, str):
        return web.json_response({'error': 'Invalid input'}, status=400)

    # Evaluate the arithmetic expression
    try:
        # Using eval is generally unsafe, but for the sake of this example,
        # we assume the input is controlled and safe. In a real-world scenario,
        # consider using a safe evaluation library or implement a parser.
        result = eval(expression, {"__builtins__": None}, {})
    except (SyntaxError, NameError, ZeroDivisionError):
        return web.json_response({'error': 'Invalid arithmetic expression'}, status=400)

    # Return the calculation result
    return web.json_response({'result': str(result)})

app = web.Application()
app.router.add_post('/calculator', calculate_expression)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)