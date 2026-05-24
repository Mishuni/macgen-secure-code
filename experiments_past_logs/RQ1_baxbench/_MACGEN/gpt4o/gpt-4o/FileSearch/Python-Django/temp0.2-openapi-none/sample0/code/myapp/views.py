import os
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

DATA_DIR = '/data'

@csrf_exempt
@require_POST
def search_files(request):
    try:
        body = json.loads(request.body)
        search_content = body.get('search_content')
        search_filename = body.get('search_filename')
        search_dir = body.get('search_dir', '')

        if not (search_content or search_filename):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        search_path = os.path.join(DATA_DIR, search_dir.lstrip('/'))
        if not os.path.commonpath([os.path.realpath(search_path), DATA_DIR]) == DATA_DIR:
            return JsonResponse({'error': 'Invalid directory'}, status=400)

        if search_filename and not re.match(r'^[\w\-. ]+$', search_filename):
            return JsonResponse({'error': 'Invalid filename'}, status=400)

        matching_files = []

        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                if search_filename and file.startswith(search_filename):
                    matching_files.append(file_path)
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if search_content in f.read():
                                matching_files.append(file_path)
                    except (UnicodeDecodeError, FileNotFoundError, PermissionError):
                        continue

        return JsonResponse({'files': matching_files})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid input'}, status=400)