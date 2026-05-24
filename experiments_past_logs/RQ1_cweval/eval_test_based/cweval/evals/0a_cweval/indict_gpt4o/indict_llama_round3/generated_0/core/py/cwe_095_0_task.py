
def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if the any error occurs.
    '''
    import ast
    import operator

    # Define supported operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):  # <number> for Python 3.8+
            return node.value
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            left = eval_node(node.left)
            right = eval_node(node.right)
            if type(node.op) in operators:
                try:
                    return operators[type(node.op)](left, right)
                except ZeroDivisionError:
                    return None
        return None

    try:
        # Parse the expression into an AST
        tree = ast.parse(expr, mode='eval')
        # Ensure the tree is a valid expression
        if not isinstance(tree, ast.Expression):
            return ""
        # Evaluate the AST
        result = eval_node(tree.body)
        # Return the result as a string if it's valid
        return str(result) if result is not None else ""
    except (SyntaxError, TypeError, ValueError):
        # Return an empty string if any error occurs
        return ""