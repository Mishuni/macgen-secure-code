import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search_files(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_content = data.get('search_content', None)
            search_filename = data.get('search_filename', None)
            search_dir = data.get('search_dir', None)

            base_path = '/data'
            search_path = os.path.join(base_path, search_dir.strip('/')) if search_dir else base_path

            if not os.path.exists(search_path):
                return JsonResponse({'files': []}, status=200)

            matched_files = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if (search_filename and file == search_filename) or (search_content and search_content in open(file_path).read()):
                        matched_files.append(file_path)

            return JsonResponse({'files': matched_files}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)