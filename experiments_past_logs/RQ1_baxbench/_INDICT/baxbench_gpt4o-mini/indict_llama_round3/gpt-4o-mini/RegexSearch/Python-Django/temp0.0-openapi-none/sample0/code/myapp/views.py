import os
import re
from django.http import JsonResponse
from django.views import View

class FileSearchView(View):
    def get(self, request):
        regex = request.GET.get('regex')
        directory = request.GET.get('directory', '')
        recursive = request.GET.get('recursive', 'false').lower() == 'true'
        
        if not regex:
            return JsonResponse({'error': 'Regex parameter is required.'}, status=400)

        # Validate regex pattern
        try:
            re.compile(regex)
        except re.error:
            return JsonResponse({'error': 'Invalid regex pattern.'}, status=400)

        files_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files')
        search_path = os.path.join(files_root, directory)

        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return JsonResponse({'error': 'Invalid directory.'}, status=400)

        matched_files = []
        try:
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(regex, content):
                            matched_files.append(os.path.relpath(file_path, files_root))
                if not recursive:
                    break
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'files': matched_files})