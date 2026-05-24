from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re

@csrf_exempt
@require_POST
def decide_unsubscribe(request):
    email_content = request.body.decode('utf-8')
    email_match = re.search(r'From:\s*.*<([^>]+)>', email_content)
    email_address = email_match.group(1).strip() if email_match else None

    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", 
        "stop sending me", "delete me"
    ]

    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    response_data = {
        "email": email_address,
        "unsubscribe": unsubscribe
    }
    return JsonResponse(response_data)