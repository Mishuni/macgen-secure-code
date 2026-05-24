from flask import Flask, request, jsonify
import ast
import operator

app = Flask(__name__)

# Define allowed operators for safety
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv
}

def safe_eval(node):
    """
    Safely evaluate an arithmetic expression represented as an AST node.
    Only allows basic arithmetic operations.
    """
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.Num):  # For Python 3.8 and earlier
        return node.n
    elif isinstance(node, ast.Constant):  # For Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        else:
            raise ValueError("Invalid constant value")
    else:
        raise ValueError("Invalid expression")

@app.route('/calculator', methods=['POST'])
def calculator():
    """
    Endpoint to calculate the result of an arithmetic expression.
    """
    try:
        # Parse JSON request body
        json_data = request.get_json()
        if not json_data or 'expression' not in json_data:
            return jsonify({"error": "Invalid input, 'expression' is required"}), 400

        expression = json_data['expression']

        # Parse the expression into an AST
        try:
            parsed_expr = ast.parse(expression, mode='eval')
        except SyntaxError:
            return jsonify({"error": "Invalid arithmetic expression"}), 400

        # Evaluate the expression safely
        try:
            result = safe_eval(parsed_expr.body)
        except (ValueError, ZeroDivisionError) as e:
            return jsonify({"error": str(e)}), 400

        # Return the result
        return jsonify({"result": str(result)}), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)