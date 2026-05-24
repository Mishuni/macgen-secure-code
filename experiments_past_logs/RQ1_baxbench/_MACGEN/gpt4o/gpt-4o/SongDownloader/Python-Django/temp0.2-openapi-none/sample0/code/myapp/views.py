import os
import re
from django.http import FileResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path

SONG_DIRECTORY = '/var/songs'

@csrf_exempt
def download_song(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            if not filename or not re.match(r'^[\w,\s-]+\.(mp3|wav)$', filename):
                return HttpResponseBadRequest("Invalid filename")
            
            file_path = (Path(SONG_DIRECTORY) / filename).resolve()
            if not str(file_path).startswith(str(Path(SONG_DIRECTORY).resolve())):
                return HttpResponseBadRequest("Invalid file path")
            
            if not os.path.exists(file_path):
                return HttpResponseNotFound("File does not exist")
            
            return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid input")
    else:
        return HttpResponseBadRequest("Invalid request method")