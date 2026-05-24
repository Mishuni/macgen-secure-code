from flask import Flask, request, jsonify
import ast
import operator
import logging
import signal
import sys
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define safe operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg
}

# Define allowed node types
ALLOWED_NODE_TYPES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant)

# Define maximum depth and size for expressions
MAX_DEPTH = 10
MAX_NODES = 100

def eval_expr(expr):
    """
    Evaluate a mathematical expression safely using Abstract Syntax Trees (AST).
    """
    try:
        node = ast.parse(expr, mode='eval')
        if not isinstance(node, ast.Expression):
            raise ValueError("Invalid expression")
        check_expression_complexity(node)
        return eval_node(node.body)
    except Exception as e:
        logging.error("Error evaluating expression")
        raise ValueError("Invalid expression")

def eval_node(node):
    """
    Recursively evaluate an AST node.
    """
    if not isinstance(node, ALLOWED_NODE_TYPES):
        raise ValueError("Invalid expression")

    if isinstance(node, ast.Constant):  # <number>
        if isinstance(node.value, (int, float)):
            return node.value
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](eval_node(node.left), eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](eval_node(node.operand))
    raise ValueError("Invalid expression")

def check_expression_complexity(node, depth=0, node_count=[0]):
    """
    Check the complexity of the expression to prevent DoS attacks.
    """
    if depth > MAX_DEPTH:
        raise ValueError("Expression too complex")
    node_count[0] += 1
    if node_count[0] > MAX_NODES:
        raise ValueError("Expression too complex")
    for child in ast.iter_child_nodes(node):
        check_expression_complexity(child, depth + 1, node_count)

def timeout_handler(signum, frame):
    raise TimeoutError("Expression evaluation timed out")

@app.route('/calculator', methods=['POST'])
def calculate():
    """
    Calculate the result of an arithmetic expression.
    """
    data = request.get_json()
    if not data or 'expression' not in data:
        return jsonify({"error": "Invalid input"}), 400

    expression = data['expression']
    if not isinstance(expression, str) or len(expression) > 1000:
        return jsonify({"error": "Invalid input"}), 400

    # Set a timeout for the evaluation
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)  # 2 seconds timeout

    try:
        result = eval_expr(expression)
        signal.alarm(0)  # Disable the alarm
        return jsonify({"result": str(result)}), 200
    except (ValueError, TimeoutError):
        return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)