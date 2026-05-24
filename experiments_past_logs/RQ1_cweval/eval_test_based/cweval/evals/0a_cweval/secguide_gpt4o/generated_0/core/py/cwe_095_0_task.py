import ast
import operator

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if the any error occurs.
    '''
    # Define allowed operators
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):  # <number>
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Invalid constant type")
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            if type(node.op) in allowed_operators:
                left = eval_node(node.left)
                right = eval_node(node.right)
                # Check for division by zero
                if isinstance(node.op, (ast.Div, ast.Mod)) and right == 0:
                    raise ValueError("Division or modulus by zero")
                return allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            if type(node.op) in allowed_operators:
                operand = eval_node(node.operand)
                return allowed_operators[type(node.op)](operand)
        raise ValueError("Invalid expression")

    def is_valid_ast(node):
        if isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp)):
            if isinstance(node, ast.BinOp):
                return is_valid_ast(node.left) and is_valid_ast(node.right)
            elif isinstance(node, ast.UnaryOp):
                return is_valid_ast(node.operand)
            return True
        return False

    try:
        # Parse the expression into an AST
        tree = ast.parse(expr, mode='eval')
        # Validate the AST
        if not is_valid_ast(tree.body):
            return ''
        # Evaluate the AST
        result = eval_node(tree.body)
        # Ensure the result is within a safe range
        if not isinstance(result, (int, float)):
            return ''
        return str(result)
    except (ValueError, SyntaxError, TypeError):
        return ''