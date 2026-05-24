import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            expression = body.get('expression', '')
            result = evaluate_expression(expression)
            return JsonResponse({'result': str(result)})
        except Exception as e:
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def evaluate_expression(expression):
    # Validate the expression to allow only numbers and basic operators
    if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expression):
        raise ValueError("Invalid characters in expression")
    
    # Evaluate the expression safely
    return eval(expression, {"__builtins__": None}, {})