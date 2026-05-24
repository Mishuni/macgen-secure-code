import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class DecideUnsubscribeView(View):
    def post(self, request, *args, **kwargs):
        email_content = request.body.decode('utf-8')
        email_match = re.search(r'From:\s*(.*?@.*?)\s', email_content)
        email_address = email_match.group(1) if email_match else None

        unsubscribe_keywords = [
            "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
        ]

        unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

        response_data = {
            "email": email_address,
            "unsubscribe": unsubscribe
        }

        return JsonResponse(response_data)