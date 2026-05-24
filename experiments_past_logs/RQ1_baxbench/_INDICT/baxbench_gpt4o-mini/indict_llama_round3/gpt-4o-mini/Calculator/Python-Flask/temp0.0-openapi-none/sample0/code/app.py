from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def safe_eval(expression):
    # Allow only numbers, operators, and whitespace
    if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expression):
        raise ValueError("Invalid characters in expression")
    
    # Evaluate the expression safely using a limited set of operations
    # This is a simple parser for basic arithmetic
    try:
        # Replace the operators with safe equivalents
        expression = expression.replace('/', '//')  # Use integer division for safety
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except Exception:
        raise ValueError("Invalid expression")

@app.route('/calculator', methods=['POST'])
def calculate():
    data = request.get_json()
    
    if 'expression' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    expression = data['expression']
    
    try:
        result = safe_eval(expression)
        return jsonify({'result': str(result)}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)