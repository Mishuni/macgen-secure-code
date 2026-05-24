from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import zipfile
import io
import os

MAX_UNCOMPRESSED_SIZE = 10 * 1024 * 1024  # 10 MB

def is_safe_path(base_path, path):
    return os.path.realpath(path).startswith(os.path.realpath(base_path))

@csrf_exempt
@require_POST
def convert_zip_to_txt(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    zip_file = request.FILES['file']

    if not zipfile.is_zipfile(zip_file):
        return JsonResponse({'error': 'Invalid zip file'}, status=400)

    try:
        with zipfile.ZipFile(zip_file) as z:
            total_uncompressed_size = 0
            text_content = []
            for file_info in z.infolist():
                if file_info.filename.endswith('.txt'):
                    if not is_safe_path('/', file_info.filename):
                        return JsonResponse({'error': 'Unsafe file path detected'}, status=400)
                    
                    total_uncompressed_size += file_info.file_size
                    if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                        return JsonResponse({'error': 'Uncompressed size exceeds limit'}, status=400)

                    with z.open(file_info) as f:
                        text_content.append(f.read().decode('utf-8'))
            return HttpResponse('\n'.join(text_content), content_type='text/plain')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)