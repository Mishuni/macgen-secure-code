import os
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Base directory for file storage
BASE_DATA_DIR = Path('/data').resolve()

@csrf_exempt
def search_files(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        # Parse JSON input
        data = json.loads(request.body)
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        # Validate and sanitize inputs
        if search_dir:
            search_dir = os.path.normpath(search_dir)
            if search_dir.startswith('..') or not (BASE_DATA_DIR / search_dir).resolve().is_relative_to(BASE_DATA_DIR):
                return JsonResponse({'error': 'Invalid search_dir'}, status=400)

        target_dir = (BASE_DATA_DIR / search_dir).resolve()
        if not target_dir.is_dir():
            return JsonResponse({'error': 'Directory does not exist'}, status=400)

        # Search for files
        matching_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                if search_filename and search_filename in file:
                    matching_files.append(str(file_path))
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if search_content in f.read():
                                matching_files.append(str(file_path))
                    except (UnicodeDecodeError, OSError):
                        continue

        return JsonResponse({'files': matching_files}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON input'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)