import os
import re
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

FILES_ROOT = os.path.join(settings.BASE_DIR, 'files')

class FileSearchView(View):
    def get(self, request):
        regex = request.GET.get('regex')
        directory = request.GET.get('directory', '')
        recursive = request.GET.get('recursive', 'false').lower() == 'true'

        if not regex:
            return JsonResponse({'error': 'Regex pattern is required.'}, status=400)

        try:
            compiled_regex = re.compile(regex)
        except re.error:
            return JsonResponse({'error': 'Invalid regex pattern.'}, status=400)

        search_path = os.path.join(FILES_ROOT, directory)
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return JsonResponse({'error': 'Directory does not exist or is not accessible.'}, status=400)

        matched_files = []
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if compiled_regex.search(content):
                            matched_files.append(os.path.relpath(file_path, start=search_path))
                except (IOError, UnicodeDecodeError):
                    continue

            if not recursive:
                break

        return JsonResponse({'files': matched_files}, status=200)