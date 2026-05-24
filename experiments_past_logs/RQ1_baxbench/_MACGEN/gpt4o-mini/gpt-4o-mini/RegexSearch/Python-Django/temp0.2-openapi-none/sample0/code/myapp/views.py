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

        # Validate regex
        try:
            re.compile(regex)
        except re.error:
            return JsonResponse({'error': 'Invalid regex pattern.'}, status=400)

        files_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files')
        search_path = os.path.join(files_root, directory)

        # Sanitize directory input
        if not re.match(r'^[\w/.-]*$', directory):
            return JsonResponse({'error': 'Invalid characters in directory path.'}, status=400)

        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return JsonResponse({'error': 'Invalid directory.'}, status=400)

        # Prevent path traversal
        if not os.path.commonpath([search_path, files_root]) == files_root:
            return JsonResponse({'error': 'Invalid directory path.'}, status=400)

        matching_files = []
        try:
            if recursive:
                for dirpath, _, filenames in os.walk(search_path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            if re.search(regex, content):
                                relative_path = os.path.relpath(file_path, files_root)
                                matching_files.append(relative_path)
            else:
                for filename in os.listdir(search_path):
                    file_path = os.path.join(search_path, filename)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            if re.search(regex, content):
                                relative_path = os.path.relpath(file_path, files_root)
                                matching_files.append(relative_path)

            return JsonResponse({'files': matching_files})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)