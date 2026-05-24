import os
import re
import json
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

        search_path = os.path.join(settings.BASE_DIR, 'files', directory)
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return JsonResponse({'error': 'Invalid directory.'}, status=400)

        matched_files = []
        if recursive:
            for root, _, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if compiled_regex.search(content):
                            matched_files.append(os.path.relpath(file_path, search_path))
        else:
            for file in os.listdir(search_path):
                file_path = os.path.join(search_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if compiled_regex.search(content):
                            matched_files.append(file)

        return JsonResponse({'files': matched_files})