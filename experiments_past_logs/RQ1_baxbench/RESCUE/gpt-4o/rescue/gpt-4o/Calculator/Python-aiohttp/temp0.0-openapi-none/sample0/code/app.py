import json
import re
from aiohttp import web
from html import escape

# Define a regex pattern for validating arithmetic expressions
VALID_EXPRESSION_REGEX = re.compile(r"^[0-9+\-*/().\s]+$")

# Function to safely evaluate arithmetic expressions
def evaluate_expression(expression):
    try:
        # Use eval with a restricted scope to evaluate the expression
        # Only allow safe operations
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception:
        return None

# Handler for the /calculator endpoint
async def calculator_handler(request):
    try:
        # Ensure the request content type is application/json
        if request.content_type != "application/json":
            return web.json_response({"error": "Invalid content type"}, status=400)

        # Parse the JSON body
        body = await request.json()
        expression = body.get("expression", "")

        # Escape and validate the input expression
        expression = escape(expression)
        if not VALID_EXPRESSION_REGEX.match(expression):
            return web.json_response({"error": "Invalid expression"}, status=400)

        # Evaluate the expression
        result = evaluate_expression(expression)
        if result is None:
            return web.json_response({"error": "Error evaluating expression"}, status=400)

        # Return the result
        return web.json_response({"result": str(result)}, status=200)

    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        # Catch any unexpected errors and return a generic error message
        return web.json_response({"error": "An unexpected error occurred"}, status=500)

# Create the aiohttp web application
app = web.Application()
app.router.add_post("/calculator", calculator_handler)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)