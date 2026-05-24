import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

LOG_FILE = 'logs.txt'

@csrf_exempt
def log_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        if not isinstance(message, str) or not message.strip():
            return JsonResponse({'error': 'Invalid message'}, status=400)
        with open(LOG_FILE, 'a') as f:
            f.write(message + '\n')
        return JsonResponse({'status': 'success'}, status=200)
    elif request.method == 'GET':
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
            return HttpResponse(logs, content_type='text/plain')
        except FileNotFoundError:
            return HttpResponse('', content_type='text/plain')
    return JsonResponse({'error': 'Method not allowed'}, status=405)