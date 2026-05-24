import re
from asteval import Interpreter

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if the any error occurs.
    '''
    if not expr:
        return ""
    
    # Enhanced validation to ensure the expression is well-formed
    if not re.match(r'^(?!.*[+\-*/]{2,})(?!^[+\-*/])(?<![+\-*/])[\d\s\+\-\*/\(\)]+(?<![+\-*/])$', expr):
        return ""
    
    aeval = Interpreter()
    
    try:
        result = aeval(expr)
        return str(result)
    except (SyntaxError, NameError):
        return ""