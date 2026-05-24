import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

SONG_DIR = '/var/songs/'

@csrf_exempt
def download_song(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename', '').strip()
            if not filename or not isinstance(filename, str):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Sanitize the filename to prevent directory traversal
            safe_filename = os.path.basename(filename)
            file_path = os.path.join(SONG_DIR, safe_filename)

            if not os.path.isfile(file_path):
                return JsonResponse({'error': 'File does not exist'}, status=404)

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                return response
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)