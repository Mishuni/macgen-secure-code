import ast
import operator
import re

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
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Define a function to evaluate the AST
    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        elif isinstance(node, ast.Num):  # for Python 3.7 and below
            return node.n
        elif isinstance(node, ast.Constant):  # for Python 3.8 and above
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            left = eval_node(node.left)
            right = eval_node(node.right)
            if isinstance(right, (int, float)) and right == 0 and isinstance(node.op, ast.Div):
                raise ZeroDivisionError("Division by zero is not allowed.")
            result = allowed_operators[type(node.op)](left, right)
            return result
        else:
            raise ValueError("Invalid expression")

    # Enhanced regex to validate the input expression
    if not re.match(r'^\s*[\d\s\+\-\*\/\(\)]+\s*$', expr) or re.search(r'[\+\-\*\/]{2,}', expr):
        return ''

    # Limit the length of the expression to prevent DoS
    if len(expr) > 100:
        return ''

    try:
        # Parse the expression into an AST
        tree = ast.parse(expr, mode='eval')
        result = eval_node(tree)
        return str(result)
    except (SyntaxError, ValueError, ZeroDivisionError):
        return ''