import ast
import operator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Allowed operators for evaluation
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(node):
    """Safely evaluate an arithmetic expression."""
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        operand = safe_eval(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)
    elif isinstance(node, ast.Num):  # For Python 3.8 and earlier
        return node.n
    elif isinstance(node, ast.Constant):  # For Python 3.9+
        return node.value
    else:
        raise ValueError("Invalid expression")

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            if not expression:
                return JsonResponse({'error': 'Invalid input'}, status=400)
            # Parse and evaluate the expression
            tree = ast.parse(expression, mode='eval')
            result = safe_eval(tree.body)
            return JsonResponse({'result': str(result)})
        except (ValueError, SyntaxError):
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)