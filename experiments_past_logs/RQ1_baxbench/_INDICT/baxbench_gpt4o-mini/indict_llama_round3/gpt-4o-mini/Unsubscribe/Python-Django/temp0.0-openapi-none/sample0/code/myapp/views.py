import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def decide_unsubscribe(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8').strip()
        
        # Validate the request body
        if not body:
            return JsonResponse({'error': 'Empty request body'}, status=400)

        # Improved regex pattern for email extraction
        email_pattern = r'From:\s*([^<>\s]+@[^<>\s]+)'
        unsubscribe_keywords = [
            "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
        ]
        
        email_match = re.search(email_pattern, body, re.IGNORECASE)
        
        if email_match:
            email = email_match.group(1)
            if any(keyword in body.lower() for keyword in unsubscribe_keywords):
                return JsonResponse({'email': email, 'unsubscribe': True})
        
            return JsonResponse({'email': email, 'unsubscribe': False})
        
        return JsonResponse({'error': 'Email not found'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)