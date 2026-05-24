import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@csrf_exempt
def decide_unsubscribe(request):
    if request.method == 'POST':
        try:
            # Parse the raw email content
            raw_email = request.body.decode('utf-8')

            # Extract the "From" email address
            from_match = re.search(r'From:\s*.*<(.+?)>', raw_email)
            if not from_match:
                return JsonResponse({'error': 'Invalid email format'}, status=400)
            email = from_match.group(1)

            # Check for unsubscribe keywords
            unsubscribe_keywords = [
                "unsubscribe", "remove me", "deregister me", 
                "stop sending me", "delete me"
            ]
            unsubscribe = any(keyword in raw_email.lower() for keyword in unsubscribe_keywords)

            # Return the response
            return JsonResponse({'email': email, 'unsubscribe': unsubscribe}, status=200)

        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)