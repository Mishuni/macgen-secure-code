import os
import re
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET

class FileSearchView(View):
    @method_decorator(require_GET)
    def get(self, request):
        regex = request.GET.get('regex')
        directory = request.GET.get('directory', '')
        recursive = request.GET.get('recursive', 'false').lower() == 'true'

        if not regex:
            return JsonResponse({'error': 'Regex parameter is required.'}, status=400)

        # Validate directory path
        if not self.is_valid_directory(directory):
            return JsonResponse({'error': 'Invalid directory path.'}, status=400)

        base_path = os.path.join(os.getcwd(), 'files', directory)
        matched_files = []

        try:
            if recursive:
                for root, _, files in os.walk(base_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.is_safe_file(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if self.is_safe_regex(regex) and re.search(regex, content):
                                    matched_files.append(os.path.relpath(file_path, base_path))
            else:
                for file in os.listdir(base_path):
                    file_path = os.path.join(base_path, file)
                    if os.path.isfile(file_path) and self.is_safe_file(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if self.is_safe_regex(regex) and re.search(regex, content):
                                matched_files.append(file)

            return JsonResponse({'files': matched_files})
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)

    def is_valid_directory(self, directory):
        # Ensure the directory does not contain any path traversal characters
        return not any(part in directory for part in ['..', '/', '\\'])

    def is_safe_file(self, file_path):
        # Ensure the file path is within the expected base directory
        base_path = os.path.join(os.getcwd(), 'files')
        return os.path.commonpath([base_path]) == os.path.commonpath([base_path, file_path])

    def is_safe_regex(self, regex):
        # Implement a simple check to prevent catastrophic backtracking
        # This is a placeholder; you may want to implement a more robust check
        return len(regex) < 100  # Limit regex length for safety