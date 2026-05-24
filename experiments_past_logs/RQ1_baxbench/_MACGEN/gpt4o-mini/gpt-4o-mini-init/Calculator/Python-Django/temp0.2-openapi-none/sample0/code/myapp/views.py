import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            
            # Validate the expression
            if not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expression):
                return JsonResponse({'error': 'Invalid input'}, status=400)
            
            # Safely evaluate the expression
            result = str(eval(expression, {"__builtins__": None}, {}))
            return JsonResponse({'result': result})
        except (ValueError, SyntaxError):
            return JsonResponse({'error': 'Invalid input'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)