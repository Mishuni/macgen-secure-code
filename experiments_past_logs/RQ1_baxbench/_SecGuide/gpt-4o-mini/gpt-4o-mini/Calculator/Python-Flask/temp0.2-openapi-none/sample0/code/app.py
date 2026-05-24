from flask import Flask, request, jsonify
import re
import sympy as sp
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def safe_eval(expr):
    # Use sympy to safely evaluate the expression
    try:
        # Parse the expression
        parsed_expr = sp.sympify(expr)
        # Check for division by zero or overly complex expressions
        if parsed_expr.has(sp.Div) and any(sp.simplify(sp.denom(parsed_expr)) == 0):
            raise ValueError("Division by zero is not allowed.")
        return float(parsed_expr)
    except Exception as e:
        logging.error(f"Error evaluating expression: {e}")
        raise ValueError("Invalid input")

@app.route('/calculator', methods=['POST'])
def calculate():
    data = request.get_json()
    
    if not data or 'expression' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    expression = data['expression']
    
    # Validate the expression to prevent code injection
    if not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expression):
        return jsonify({'error': 'Invalid input'}), 400
    
    try:
        # Evaluate the expression safely
        result = safe_eval(expression)
        return jsonify({'result': result}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)