import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import ast
import operator

# Define supported operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def eval_expr(expr):
    """
    Evaluate a mathematical expression safely using AST.
    """
    def _eval(node):
        if isinstance(node, ast.Constant):  # <number>
            return node.value
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            return OPERATORS[type(node.op)](_eval(node.operand))
        else:
            raise TypeError(node)

    return _eval(ast.parse(expr, mode='eval').body)

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            # Evaluate the expression safely
            result = eval_expr(expression)
            return JsonResponse({'result': str(result)}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)