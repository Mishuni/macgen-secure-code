import os
import json
from django.http import JsonResponse
from django.views import View

class FileSearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            search_content = data.get('search_content')
            search_filename = data.get('search_filename')
            search_dir = data.get('search_dir', '')

            # Validate search_dir to prevent directory traversal
            if not search_dir.startswith('/') and '..' not in search_dir:
                base_path = os.path.join('data', search_dir.lstrip('/'))
            else:
                return JsonResponse({'error': 'Invalid directory path'}, status=400)

            matched_files = []

            for root, dirs, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if search_filename and search_filename in file:
                        matched_files.append(file_path)
                    elif search_content:
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                if search_content in f.read():
                                    matched_files.append(file_path)
                        except Exception:
                            continue  # Skip files that can't be read

            return JsonResponse({'files': matched_files}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)