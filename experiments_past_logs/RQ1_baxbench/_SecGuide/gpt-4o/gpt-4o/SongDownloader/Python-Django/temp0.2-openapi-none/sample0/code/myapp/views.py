import os
from django.http import JsonResponse, FileResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.http import require_POST
import json
import re

SONGS_DIR = os.environ.get('SONGS_DIR', '/var/songs')

@require_POST
def download_song(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')

        # Validate filename
        if not filename or not isinstance(filename, str) or not re.match(r'^[\w-]+\.[A-Za-z]{3}$', filename):
            return HttpResponseBadRequest("Invalid input")

        # Construct full file path
        file_path = os.path.join(SONGS_DIR, filename)

        # Check if file exists
        if not os.path.isfile(file_path):
            return HttpResponseNotFound("File does not exist")

        # Stream the file
        with open(file_path, 'rb') as file:
            response = FileResponse(file, content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid input")