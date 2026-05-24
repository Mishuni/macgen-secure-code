import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def decide_unsubscribe(request):
    if request.method == 'POST':
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        body = request.body.decode('utf-8')
        email_match = re.search(email_pattern, body)
        email = email_match.group(0) if email_match else None

        unsubscribe_keywords = [
            "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
        ]
        unsubscribe = any(keyword in body.lower() for keyword in unsubscribe_keywords)

        return JsonResponse({
            'email': email,
            'unsubscribe': unsubscribe
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)