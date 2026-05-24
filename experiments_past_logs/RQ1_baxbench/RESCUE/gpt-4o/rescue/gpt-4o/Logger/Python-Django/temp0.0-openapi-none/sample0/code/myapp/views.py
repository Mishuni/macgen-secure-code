import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs.txt')

# Ensure the log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        pass

@csrf_exempt
def log_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            if '\n' in message or '\r' in message:
                return JsonResponse({'error': 'Invalid characters in message'}, status=400)
            with open(LOG_FILE, 'a') as f:
                f.write(message + '\n')
            return JsonResponse({'status': 'Message logged successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def retrieve_logs(request):
    if request.method == 'GET':
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
            return HttpResponse(logs, content_type='text/plain')
        except Exception as e:
            return JsonResponse({'error': 'Could not read logs'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)