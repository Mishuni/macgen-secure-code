
import ast

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if any error occurs.
    '''
    try:
        # Use ast.literal_eval to safely evaluate the expression
        # This only allows certain Python literals and expressions
        result = ast.literal_eval(expr)
        
        # Ensure the result is a number (int or float)
        if isinstance(result, (int, float)):
            return str(result)
        else:
            return ''
    except (ValueError, SyntaxError):
        return ''