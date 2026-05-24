import re
from django.http import JsonResponse
from django.views import View

class DecideUnsubscribeView(View):
    UNSUBSCRIBE_KEYWORDS = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ]

    def post(self, request):
        # Get the raw email content from the request body
        email_content = request.body.decode('utf-8')

        # Validate the input
        if not isinstance(email_content, str) or not email_content.strip():
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Check for unsubscribe keywords
        should_unsubscribe = any(keyword in email_content.lower() for keyword in self.UNSUBSCRIBE_KEYWORDS)

        # Extract email address from the 'From' header
        from_header = re.search(r'From:\s*([^<]+<([^>]+)>)', email_content)
        email_address = from_header.group(2) if from_header else None

        if email_address:
            return JsonResponse({
                'email': email_address,
                'unsubscribe': should_unsubscribe
            })
        else:
            return JsonResponse({'error': 'Email address not found'}, status=400)