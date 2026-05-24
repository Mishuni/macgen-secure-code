import json
import os
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.html import escape

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'logs.txt')

class LogView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            if not isinstance(message, str):
                return JsonResponse({'error': 'Invalid message format'}, status=400)

            # Sanitize the message before logging
            sanitized_message = escape(message)

            with open(LOG_FILE_PATH, 'a') as log_file:
                log_file.write(sanitized_message + '\n')

            return JsonResponse({'status': 'Log message successful'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        try:
            with open(LOG_FILE_PATH, 'r') as log_file:
                logs = log_file.read()
            return HttpResponse(logs, content_type='text/plain')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)