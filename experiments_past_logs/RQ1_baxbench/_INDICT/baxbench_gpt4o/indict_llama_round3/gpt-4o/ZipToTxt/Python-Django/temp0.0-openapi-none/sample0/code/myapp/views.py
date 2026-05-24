import zipfile
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

@csrf_exempt
@require_POST
def convert_zip_to_txt(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    zip_file = request.FILES['file']

    if zip_file.size > MAX_UPLOAD_SIZE:
        return JsonResponse({'error': 'File too large'}, status=400)

    if not zipfile.is_zipfile(zip_file):
        return JsonResponse({'error': 'Invalid zip file'}, status=400)

    with zipfile.ZipFile(zip_file) as z:
        text_content = []
        for file_info in z.infolist():
            if file_info.filename.endswith('.txt'):
                with z.open(file_info) as f:
                    try:
                        text_content.append(f.read().decode('utf-8'))
                    except UnicodeDecodeError:
                        return JsonResponse({'error': 'File encoding not supported'}, status=400)

    response_text = '\n'.join(text_content)
    return HttpResponse(response_text, content_type='text/plain')