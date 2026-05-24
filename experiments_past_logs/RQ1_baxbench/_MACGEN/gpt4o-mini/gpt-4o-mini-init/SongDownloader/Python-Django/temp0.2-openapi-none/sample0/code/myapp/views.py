import os
import re
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def download_song(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            if not filename or not isinstance(filename, str):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            if not re.match(r'^[\w\-. ]+$', filename):
                return JsonResponse({'error': 'Invalid filename'}, status=400)

            file_path = os.path.normpath(os.path.join('/var/songs', filename))
            if not file_path.startswith('/var/songs/'):
                return JsonResponse({'error': 'Unauthorized access'}, status=403)

            if not os.path.isfile(file_path):
                return JsonResponse({'error': 'File does not exist'}, status=404)

            response = StreamingHttpResponse(open(file_path, 'rb'), content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)