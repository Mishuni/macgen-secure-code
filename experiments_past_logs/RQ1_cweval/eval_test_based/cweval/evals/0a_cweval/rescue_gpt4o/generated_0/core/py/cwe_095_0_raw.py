
import subprocess

def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if any error occurs.
    '''
    try:
        # Validate and sanitize the input to ensure it only contains valid arithmetic characters
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in expr):
            return ""

        # Use subprocess to securely evaluate the expression using the `bc` command
        result = subprocess.run(
            ['bc', '-l'],  # Use `bc` in math mode
            input=expr.encode('utf-8'),  # Pass the expression as input
            stdout=subprocess.PIPE,  # Capture the output
            stderr=subprocess.PIPE,  # Capture any errors
            check=True  # Raise an exception if the command fails
        )

        # Decode and strip the output to get the result
        output = result.stdout.decode('utf-8').strip()

        # Return the result if it is valid, otherwise return an empty string
        return output if output else ""
    except (subprocess.CalledProcessError, ValueError, OSError):
        # Gracefully handle any errors and return an empty string
        return ""