import os
import json
from django.http import JsonResponse, BadRequest
from django.views.decorators.csrf import csrf_exempt

DATA_DIR = '/data'

@csrf_exempt
def search_files(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            search_content = body.get('search_content', None)
            search_filename = body.get('search_filename', None)
            search_dir = body.get('search_dir', None)

            # Validate and sanitize inputs
            if search_dir and not search_dir.startswith('/'):
                raise ValueError("Invalid directory path")
            if search_dir and '..' in search_dir:
                raise ValueError("Directory traversal attempt detected")

            search_path = os.path.join(DATA_DIR, search_dir) if search_dir else DATA_DIR
            if not os.path.exists(search_path):
                return JsonResponse({'files': []})

            matched_files = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if (search_filename and file == search_filename) or \
                       (search_content and search_filename is None and search_content in open(file_path).read()):
                        matched_files.append(file_path)

            return JsonResponse({'files': matched_files})

        except ValueError as e:
            return BadRequest(f"Invalid input: {str(e)}")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)