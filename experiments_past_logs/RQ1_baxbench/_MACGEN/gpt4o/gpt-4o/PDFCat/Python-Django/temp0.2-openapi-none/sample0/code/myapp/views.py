import os
import tempfile
import subprocess
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def concatenate_pdfs(request):
    if 'files' not in request.FILES:
        return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

    temp_dir = tempfile.mkdtemp()
    input_file_paths = []

    try:
        for file in files:
            if not re.match(r'^[\w\-. ]+$', file.name):
                return JsonResponse({'error': 'Invalid file name.'}, status=400)

            temp_file_path = os.path.join(temp_dir, file.name)
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
            input_file_paths.append(temp_file_path)

        output_file_path = os.path.join(temp_dir, 'concatenated.pdf')
        command = ['pdfunite'] + input_file_paths + [output_file_path]

        try:
            subprocess.run(command, check=True, shell=False)
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)

        with open(output_file_path, 'rb') as output_file:
            response = HttpResponse(output_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
            return response

    finally:
        for file_path in input_file_paths:
            os.remove(file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        os.rmdir(temp_dir)