import os
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

        if search_content is None and search_filename is None:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Sanitize search_dir to prevent directory traversal
        search_dir = os.path.normpath(search_dir).lstrip(os.sep)
        search_path = os.path.join(DATA_DIR, search_dir)

        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return JsonResponse({'files': []})

        matching_files = []

        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                if search_filename and file.startswith(search_filename):
                    matching_files.append(file_path)
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                if search_content in line:
                                    matching_files.append(file_path)
                                    break
                    except (IOError, OSError):
                        continue

        return JsonResponse({'files': matching_files})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid input'}, status=400)