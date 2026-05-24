import os
import re
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET

FILES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files')

@method_decorator(require_GET, name='dispatch')
class FileSearchView(View):
    def get(self, request):
        regex = request.GET.get('regex')
        directory = request.GET.get('directory', '')
        recursive = request.GET.get('recursive', 'false').lower() == 'true'

        if not regex:
            return JsonResponse({'error': 'Regex parameter is required.'}, status=400)

        # Validate directory input
        if not self.is_safe_directory(directory):
            return JsonResponse({'error': 'Invalid directory.'}, status=400)

        # Search files
        try:
            matched_files = self.search_files(regex, directory, recursive)
            return JsonResponse({'files': matched_files})
        except re.error:
            return JsonResponse({'error': 'Invalid regex pattern.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def is_safe_directory(self, directory):
        # Ensure the directory is safe and within the FILES_ROOT
        safe_path = os.path.abspath(os.path.join(FILES_ROOT, directory))
        return safe_path.startswith(os.path.abspath(FILES_ROOT))

    def search_files(self, regex, directory, recursive):
        matched_files = []
        search_path = os.path.join(FILES_ROOT, directory)

        if recursive:
            for root, _, files in os.walk(search_path):
                for file in files:
                    if self.file_matches_regex(os.path.join(root, file), regex):
                        matched_files.append(os.path.relpath(os.path.join(root, file), FILES_ROOT))
        else:
            for file in os.listdir(search_path):
                if self.file_matches_regex(os.path.join(search_path, file), regex):
                    matched_files.append(os.path.relpath(os.path.join(search_path, file), FILES_ROOT))

        return matched_files

    def file_matches_regex(self, file_path, regex):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return re.search(regex, content) is not None
        except Exception:
            return False