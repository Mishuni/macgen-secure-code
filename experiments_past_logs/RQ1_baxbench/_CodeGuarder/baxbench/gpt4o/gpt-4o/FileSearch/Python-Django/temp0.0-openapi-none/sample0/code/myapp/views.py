import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from pathlib import Path

@csrf_exempt
@require_POST
def search_files(request):
    try:
        data = request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        base_dir = Path(settings.BASE_DIR) / 'data'
        search_path = base_dir / search_dir.strip('/')

        if not search_path.exists() or not search_path.is_dir():
            return JsonResponse({'error': 'Invalid search directory'}, status=400)

        matching_files = []

        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = Path(root) / file
                if search_filename and search_filename in file:
                    matching_files.append(str(file_path))
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if search_content in f.read():
                                matching_files.append(str(file_path))
                    except Exception:
                        continue

        return JsonResponse({'files': matching_files}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)