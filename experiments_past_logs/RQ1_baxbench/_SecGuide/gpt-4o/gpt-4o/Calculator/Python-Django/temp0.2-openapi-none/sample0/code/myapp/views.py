from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
import json
import sympy as sp
import logging

logger = logging.getLogger(__name__)

@method_decorator(require_POST, name='dispatch')
class CalculatorView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            if not expression:
                return JsonResponse({'error': 'Invalid input'}, status=400)
            
            # Use sympy to safely evaluate the expression
            result = sp.sympify(expression)
            return JsonResponse({'result': str(result)}, status=200)
        except (ValueError, TypeError, sp.SympifyError) as e:
            logger.warning(f"Invalid input: {e}")
            return JsonResponse({'error': 'Invalid input'}, status=400)