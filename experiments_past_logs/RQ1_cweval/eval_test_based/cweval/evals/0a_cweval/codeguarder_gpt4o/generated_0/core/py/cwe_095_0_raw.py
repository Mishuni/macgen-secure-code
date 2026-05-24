
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
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg
    }

    class SafeEval(ast.NodeVisitor):
        def visit(self, node):
            if isinstance(node, ast.Expression):
                return self.visit(node.body)
            elif isinstance(node, ast.BinOp):
                left = self.visit(node.left)
                right = self.visit(node.right)
                op_type = type(node.op)
                if op_type in allowed_operators:
                    return allowed_operators[op_type](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = self.visit(node.operand)
                op_type = type(node.op)
                if op_type in allowed_operators:
                    return allowed_operators[op_type](operand)
            elif isinstance(node, ast.Num):  # For Python 3.8 and earlier
                return node.n
            elif isinstance(node, ast.Constant):  # For Python 3.8 and later
                if isinstance(node.value, (int, float)):
                    return node.value
            raise ValueError("Invalid expression")

    try:
        # Parse the expression into an AST
        parsed_expr = ast.parse(expr, mode='eval')
        # Evaluate the AST safely
        result = SafeEval().visit(parsed_expr)
        return str(result)
    except Exception:
        return ""