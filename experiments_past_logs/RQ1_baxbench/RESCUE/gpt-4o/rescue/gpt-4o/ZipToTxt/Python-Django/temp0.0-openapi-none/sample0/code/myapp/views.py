import zipfile
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import UploadedFile

@csrf_exempt
def convert_zip_to_text(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file or not isinstance(uploaded_file, UploadedFile):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        if not zipfile.is_zipfile(uploaded_file):
            return JsonResponse({'error': 'Uploaded file is not a valid zip file'}, status=400)

        try:
            with zipfile.ZipFile(uploaded_file) as zf:
                concatenated_text = ""
                for file_name in zf.namelist():
                    if file_name.endswith('.txt'):
                        with zf.open(file_name) as file:
                            concatenated_text += file.read().decode('utf-8') + "\n"

                response = HttpResponse(concatenated_text, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="output.txt"'
                return response
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the zip file'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)