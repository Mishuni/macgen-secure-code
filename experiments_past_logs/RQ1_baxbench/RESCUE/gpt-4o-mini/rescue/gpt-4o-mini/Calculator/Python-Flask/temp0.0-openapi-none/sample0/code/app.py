from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calculator', methods=['POST'])
def calculate():
    json_data = request.get_json()
    
    # Validate input
    if 'expression' not in json_data or not isinstance(json_data['expression'], str):
        return jsonify({"msg": "Invalid input"}), 400
    
    expression = json_data['expression']
    
    # Evaluate the expression safely
    try:
        # Using eval is dangerous; instead, we will use a safer approach
        # Here we will only allow basic arithmetic operations
        allowed_operators = {'+', '-', '*', '/'}
        if any(op not in allowed_operators for op in expression if op in allowed_operators):
            return jsonify({"msg": "Invalid input"}), 400
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": None}, {})
        
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"msg": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)