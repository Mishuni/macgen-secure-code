import os
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search_files(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_content = data.get('search_content')
            search_filename = data.get('search_filename')
            search_dir = data.get('search_dir', '')

            # Validate search_dir to prevent path traversal
            if not re.match(r'^[\w\-]*$', search_dir) or '..' in search_dir:  # Only allow alphanumeric and hyphen, disallow path traversal
                return JsonResponse({'error': 'Invalid directory name'}, status=400)

            base_path = os.path.abspath(os.path.join('/data', search_dir.lstrip('/')))
            if not base_path.startswith('/data'):
                return JsonResponse({'error': 'Access denied'}, status=403)

            files_found = []
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if (search_content and search_content in open(file_path).read()) or \
                       (search_filename and file.startswith(search_filename)):
                        files_found.append(file_path)

            return JsonResponse({'files': files_found}, status=200)

        except (json.JSONDecodeError, IOError, OSError) as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)