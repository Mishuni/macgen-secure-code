import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_protect
import json
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

@csrf_protect
@require_http_methods(["POST"])
def log_message(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if message:
            logger.info(message)
            return JsonResponse({'status': 'success', 'message': 'Log message successful'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'No message provided'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

@require_http_methods(["GET"])
def retrieve_logs(request):
    # Restrict access to logs by checking user permissions (e.g., is_staff)
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized access'}, status=403)

    log_file_path = logger.handlers[0].baseFilename
    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read()
        return HttpResponse(logs, content_type='text/plain', status=200)
    except FileNotFoundError:
        return HttpResponse('', content_type='text/plain', status=200)