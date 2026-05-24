from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)

# Configure secure session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_sessions')
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

@app.route('/calculator', methods=['POST'])
def calculate():
    # Validate content-type
    if request.headers.get('Content-Type') != 'application/json':
        abort(400, description='Invalid content-type')

    # Parse and validate request body
    data = request.get_json()
    if not data or 'expression' not in data:
        abort(400, description='Invalid input')

    expression = data['expression']

    # Evaluate the arithmetic expression safely
    try:
        # Only allow safe characters
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in expression):
            abort(400, description='Invalid characters in expression')

        # Evaluate the expression
        result = eval(expression, {"__builtins__": None}, {})
    except ZeroDivisionError:
        abort(400, description='Division by zero')
    except Exception as e:
        abort(400, description='Invalid expression')

    # Return the calculation result
    return jsonify({'result': str(result)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)