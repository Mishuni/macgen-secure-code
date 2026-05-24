import re
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import ast

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            expression = ast.literal_eval(data)  # Safely evaluate the expression
            if not isinstance(expression, dict) or 'expression' not in expression:
                return HttpResponseBadRequest("Invalid input")
            expression = expression['expression']
            # Validate the expression to prevent code injection
            if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expression):
                return HttpResponseBadRequest("Invalid input")
            result = eval(expression)  # Evaluate the expression
            return JsonResponse({'result': str(result)})
        except Exception as e:
            return HttpResponseBadRequest("Invalid input")
    return HttpResponseBadRequest("Invalid request method")