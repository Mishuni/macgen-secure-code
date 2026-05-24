from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def safe_eval(expression):
    # Define allowed characters and operators
    allowed_chars = re.compile(r'^[0-9+\-*/(). ]+$')
    
    # Validate the expression
    if not allowed_chars.match(expression):
        raise ValueError("Invalid characters in expression")
    
    # Evaluate the expression safely
    try:
        # Use eval in a restricted environment
        result = eval(expression, {"__builtins__": None}, {})
    except Exception as e:
        raise ValueError("Error evaluating expression")
    
    return result

@app.route('/calculator', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        # Evaluate the expression
        result = safe_eval(expression)
        
        return jsonify({"result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)