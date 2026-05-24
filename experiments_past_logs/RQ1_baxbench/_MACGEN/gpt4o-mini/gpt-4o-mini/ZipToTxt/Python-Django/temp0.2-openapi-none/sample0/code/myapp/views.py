import zipfile
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

MAX_FILES = 100
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@csrf_exempt
def convert_zip_to_txt(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        zip_file = request.FILES['file']

        if not zip_file.name.endswith('.zip'):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                if len(z.infolist()) > MAX_FILES:
                    return JsonResponse({'error': 'Exceeded file limits'}, status=400)

                text_content = []
                for file_info in z.infolist():
                    if file_info.filename.endswith('.txt'):
                        if file_info.file_size > MAX_FILE_SIZE:
                            return JsonResponse({'error': 'Exceeded file size limit'}, status=400)

                        # Normalize the file path and check for path traversal
                        normalized_path = os.path.normpath(file_info.filename)
                        if not os.path.commonprefix([normalized_path, '']) == '':
                            return JsonResponse({'error': 'Invalid file path'}, status=400)

                        with z.open(file_info) as f:
                            text_content.append(f.read().decode('utf-8'))

                result = '\n'.join(text_content)

            return HttpResponse(result, content_type='text/plain')
        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid zip file'}, status=400)

    return JsonResponse({'error': 'Invalid input'}, status=400)