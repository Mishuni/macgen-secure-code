import subprocess
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def convert_pdf_to_text(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        pdf_file = request.FILES['file']
        
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        pdf_file_path = Path('/tmp') / pdf_file.name
        
        with open(pdf_file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        try:
            text_output = subprocess.check_output(['pdftotext', str(pdf_file_path), '-'])
            return JsonResponse(text_output.decode('utf-8'), safe=False, status=200)
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Conversion failed'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)