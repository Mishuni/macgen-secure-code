import os
import re
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.utils.html import escape

FILES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

@require_GET
def search_files(request):
    regex = request.GET.get('regex')
    directory = request.GET.get('directory', '')
    recursive = request.GET.get('recursive', 'false').lower() == 'true'

    # Validate and sanitize inputs
    if not regex:
        return HttpResponseBadRequest(JsonResponse({'error': 'The "regex" parameter is required.'}))
    try:
        re.compile(regex)
    except re.error:
        return HttpResponseBadRequest(JsonResponse({'error': 'Invalid regex pattern.'}))

    sanitized_directory = os.path.normpath(escape(directory))
    search_path = os.path.join(FILES_ROOT, sanitized_directory)

    if not os.path.commonpath([FILES_ROOT, search_path]).startswith(FILES_ROOT):
        return HttpResponseBadRequest(JsonResponse({'error': 'Invalid directory path.'}))

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return HttpResponseBadRequest(JsonResponse({'error': 'Directory does not exist.'}))

    matching_files = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(regex, content):
                        relative_path = os.path.relpath(file_path, FILES_ROOT)
                        matching_files.append(relative_path)
            except (IOError, UnicodeDecodeError):
                continue
        if not recursive:
            break

    return JsonResponse({'files': matching_files})