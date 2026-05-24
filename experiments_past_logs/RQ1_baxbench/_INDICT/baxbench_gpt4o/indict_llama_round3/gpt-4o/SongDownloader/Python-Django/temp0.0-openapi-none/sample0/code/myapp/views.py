import os
import re
from django.http import JsonResponse, FileResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

SONG_DIRECTORY = '/var/songs'

@csrf_exempt
def download_song(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            if not filename or not re.match(r'^[\w,\s-]+\.[A-Za-z]{3,4}$', filename):
                return HttpResponseBadRequest("Invalid input")
            
            file_path = os.path.join(SONG_DIRECTORY, filename)
            if not os.path.exists(file_path):
                return HttpResponseNotFound("File does not exist")
            
            return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid input")
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)