import os
import zipfile
from django.http import HttpResponse, JsonResponse
from django.views import View

class ConvertZipToTextView(View):
    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        zip_file = request.FILES['file']
        if not zip_file.name.endswith('.zip'):
            return JsonResponse({'error': 'File is not a zip file'}, status=400)

        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                text_content = []
                for file_info in z.infolist():
                    if file_info.filename.endswith('.txt'):
                        with z.open(file_info) as f:
                            text_content.append(f.read().decode('utf-8'))
                concatenated_text = '\n'.join(text_content)

            return HttpResponse(concatenated_text, content_type='text/plain')
        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid zip file'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)