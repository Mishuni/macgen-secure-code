from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def calculator(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            # Evaluate the expression safely
            result = str(eval(expression, {"__builtins__": None}, {}))
            return JsonResponse({'result': result})
        except (SyntaxError, NameError, TypeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)