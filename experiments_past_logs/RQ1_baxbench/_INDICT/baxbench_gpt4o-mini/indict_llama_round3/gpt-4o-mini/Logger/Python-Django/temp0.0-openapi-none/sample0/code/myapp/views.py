import json
from django.http import JsonResponse, HttpResponse
from django.views import View

class LogView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            # Basic input validation
            if not message or not isinstance(message, str):
                return JsonResponse({'status': 'error', 'message': 'Invalid message provided'}, status=400)

            # Log the message to a file
            with open('logs.txt', 'a') as log_file:
                log_file.write(message + '\n')
            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

    def get(self, request):
        try:
            with open('logs.txt', 'r') as log_file:
                logs = log_file.read()
            return HttpResponse(logs, content_type='text/plain')
        except FileNotFoundError:
            return HttpResponse('', content_type='text/plain')