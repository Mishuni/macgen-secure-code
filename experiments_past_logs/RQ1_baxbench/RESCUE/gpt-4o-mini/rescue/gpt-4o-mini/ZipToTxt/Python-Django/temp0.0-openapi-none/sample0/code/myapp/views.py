import os
import zipfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

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
                text_content = []
                for file_info in z.infolist():
                    if file_info.filename.endswith('.txt'):
                        with z.open(file_info) as f:
                            text_content.append(f.read().decode('utf-8'))
                result = "\n".join(text_content)

            response = HttpResponse(result, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="output.txt"'
            return response

        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid zip file'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)