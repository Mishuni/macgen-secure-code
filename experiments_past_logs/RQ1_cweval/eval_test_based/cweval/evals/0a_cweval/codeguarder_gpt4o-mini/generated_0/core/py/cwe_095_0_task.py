
import re

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if any error occurs.
    '''
    # Define a safe regex pattern for valid arithmetic expressions
    safe_regex_pattern = r'^[\d\s\+\-\*\/\(\)]+$'
    
    # Validate the input expression against the safe regex pattern
    if not isinstance(expr, str) or not expr.strip() or not re.match(safe_regex_pattern, expr):
        return ''

    try:
        # Evaluate the expression safely using eval
        result = eval(expr, {"__builtins__": None}, {})
        return str(result)
    except Exception:
        return ''