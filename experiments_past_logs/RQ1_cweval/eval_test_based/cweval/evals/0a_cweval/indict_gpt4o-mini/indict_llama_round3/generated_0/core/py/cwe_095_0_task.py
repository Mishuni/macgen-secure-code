
import ast
import operator
import re

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if any error occurs.
    '''
    
    # Validate the expression to ensure it only contains valid characters
    if not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expr):
        return ''
    
    # Define a safe evaluation function using AST
    def safe_eval(node):
        if isinstance(node, ast.Expression):
            return safe_eval(node.body)
        elif isinstance(node, ast.Constant):  # for Python 3.8 and later
            return node.value
        elif isinstance(node, ast.Num):  # for Python 3.7 and earlier
            return node.n
        elif isinstance(node, ast.BinOp):
            left = safe_eval(node.left)
            right = safe_eval(node.right)
            if isinstance(node.op, ast.Add):
                return operator.add(left, right)
            elif isinstance(node.op, ast.Sub):
                return operator.sub(left, right)
            elif isinstance(node.op, ast.Mult):
                return operator.mul(left, right)
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return operator.truediv(left, right)
            elif isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return operator.floordiv(left, right)
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return operator.mod(left, right)
            elif isinstance(node.op, ast.Pow):
                return operator.pow(left, right)
            else:
                raise ValueError("Unsupported operation")
        else:
            raise ValueError("Unsupported expression")

    # Parse the expression into an AST
    try:
        tree = ast.parse(expr, mode='eval')
        result = safe_eval(tree)
        return str(result)
    except (SyntaxError, ValueError, ZeroDivisionError):
        return ''