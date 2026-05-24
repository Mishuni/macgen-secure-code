import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def decide_unsubscribe(request):
    if request.method == 'POST':
        email_content = request.body.decode('utf-8').strip()
        
        # Check for unsubscribe keywords
        unsubscribe_keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
        if any(keyword in email_content.lower() for keyword in unsubscribe_keywords):
            # Extract email from the 'From' header
            match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+\.[^<>\s]+)', email_content)
            if match:
                email = match.group(1)
                # Validate email format
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return JsonResponse({'error': 'Invalid email address'}, status=400)
                
                return JsonResponse({'email': email, 'unsubscribe': True})
        
        return JsonResponse({'email': '', 'unsubscribe': False})
    return JsonResponse({'error': 'Invalid request method'}, status=405)