import os
import tempfile
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

@csrf_exempt
@require_POST
def concatenate_pdfs(request):
    try:
        files = request.FILES.getlist('files')
        if not files or not all(isinstance(f, UploadedFile) for f in files):
            return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

        with tempfile.TemporaryDirectory() as temp_dir:
            input_paths = []
            for file in files:
                temp_file_path = os.path.join(temp_dir, file.name)
                with open(temp_file_path, 'wb') as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                input_paths.append(temp_file_path)

            output_path = os.path.join(temp_dir, 'concatenated.pdf')
            subprocess.run(['pdfunite'] + input_paths + [output_path], check=True)

            with open(output_path, 'rb') as output_file:
                response = HttpResponse(output_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)