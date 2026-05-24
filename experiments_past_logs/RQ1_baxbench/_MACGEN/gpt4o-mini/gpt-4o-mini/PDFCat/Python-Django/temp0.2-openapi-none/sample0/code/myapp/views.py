import os
import subprocess
from pathlib import Path
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

MAX_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@csrf_exempt
def concatenate_pdfs(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        
        if len(files) > MAX_FILES or any(file.size > MAX_FILE_SIZE for file in files):
            return JsonResponse({'error': 'Too many files or file too large.'}, status=400)

        input_files = []
        for pdf_file in files:
            if not pdf_file.name.endswith('.pdf'):
                return JsonResponse({'error': 'Invalid file type.'}, status=400)
            input_files.append(Path(pdf_file.temporary_file_path()).resolve())

        output_file = Path('/tmp/concatenated.pdf')
        command = ['pdfunite'] + [str(file) for file in input_files] + [str(output_file)]
        
        try:
            subprocess.run(command, check=True)
            with open(output_file, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)