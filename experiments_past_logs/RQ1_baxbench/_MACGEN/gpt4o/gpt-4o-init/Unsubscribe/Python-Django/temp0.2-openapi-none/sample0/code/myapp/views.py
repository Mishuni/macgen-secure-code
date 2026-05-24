import re
import unicodedata
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def decide_unsubscribe(request):
    raw_email = unicodedata.normalize("NFC", request.body.decode('utf-8'))
    email_match = re.search(r'From:\s*([^<]+<[^>]+>)', raw_email)
    email_address = email_match.group(1) if email_match else None

    if email_address and not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
        return JsonResponse({"error": "Invalid email format"}, status=400)

    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]

    unsubscribe = any(keyword in raw_email.lower() for keyword in unsubscribe_keywords)

    response_data = {
        "email": email_address,
        "unsubscribe": unsubscribe
    }

    return JsonResponse(response_data)