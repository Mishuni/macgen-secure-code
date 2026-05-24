from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import ast
import operator

def safe_eval(expr):
    allowed_operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    
    def eval_node(node):
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.Num):
            return node.n
        else:
            raise ValueError("Invalid expression")
    
    tree = ast.parse(expr, mode='eval')
    return eval_node(tree.body)

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            # Validate input
            if not all(c.isdigit() or c in '+-*/ ' for c in expression):
                raise ValueError("Invalid characters in expression")
            # Evaluate the expression safely
            result = safe_eval(expression)
            return JsonResponse({'result': str(result)}, status=200)
        except (SyntaxError, ValueError):
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)