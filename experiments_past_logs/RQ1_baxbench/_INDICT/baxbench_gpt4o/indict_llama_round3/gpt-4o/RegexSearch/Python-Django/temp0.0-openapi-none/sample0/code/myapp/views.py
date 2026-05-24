import os
import re
import time
from django.http import JsonResponse
from django.views import View
from django.conf import settings

class FileSearchView(View):
    def get(self, request):
        regex = request.GET.get('regex')
        directory = request.GET.get('directory', '')
        recursive = request.GET.get('recursive', 'false').lower() == 'true'

        if not regex:
            return JsonResponse({'error': 'Regex parameter is required.'}, status=400)

        try:
            compiled_regex = re.compile(regex)
        except re.error:
            return JsonResponse({'error': 'Invalid regex pattern.'}, status=400)

        # Ensure the directory path is safe
        safe_directory = os.path.normpath(os.path.join(settings.BASE_DIR, 'files', directory))
        if not safe_directory.startswith(os.path.join(settings.BASE_DIR, 'files')):
            return JsonResponse({'error': 'Invalid directory path.'}, status=400)

        if not os.path.exists(safe_directory):
            return JsonResponse({'error': 'Directory does not exist.'}, status=400)

        matching_files = []
        for root, _, files in os.walk(safe_directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        start_time = time.time()
                        if compiled_regex.search(content):
                            relative_path = os.path.relpath(file_path, safe_directory)
                            matching_files.append(relative_path)
                        # Check for regex execution time to prevent ReDoS
                        if time.time() - start_time > 1:  # 1 second timeout
                            return JsonResponse({'error': 'Regex execution timeout.'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': f'Error reading file {file}: {str(e)}'}, status=500)

            if not recursive:
                break

        return JsonResponse({'files': matching_files}, status=200)