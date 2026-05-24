import os
from django.http import JsonResponse, FileResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

SONGS_DIR = '/var/songs'

@csrf_exempt
@require_POST
def download_song(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename')
        if not filename:
            return HttpResponseBadRequest("Invalid input: 'filename' is required.")
        
        file_path = os.path.join(SONGS_DIR, filename)
        
        if not os.path.exists(file_path):
            return HttpResponseNotFound("File does not exist.")
        
        return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON input.")