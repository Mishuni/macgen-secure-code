import os
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from werkzeug.utils import secure_filename

# Directory where songs are stored
SONG_DIRECTORY = '/var/songs'

@csrf_exempt
def download_song(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        # Parse JSON body
        body = json.loads(request.body)
        filename = body.get('filename', '')

        # Validate filename
        if not filename or not isinstance(filename, str):
            return JsonResponse({'error': 'Invalid filename'}, status=400)

        # Secure the filename
        filename = secure_filename(filename)

        # Construct the full file path
        file_path = os.path.join(SONG_DIRECTORY, filename)

        # Check if the file exists and is within the SONG_DIRECTORY
        if not os.path.isfile(file_path) or not file_path.startswith(SONG_DIRECTORY):
            return JsonResponse({'error': 'File not found'}, status=404)

        # Stream the file as a response
        response = FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON input'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)