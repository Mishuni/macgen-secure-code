import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def convert_pdf_to_text(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        pdf_file = request.FILES['file']

        # Validate file type
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Invalid file type. Only PDF files are allowed.'}, status=400)

        # Save the file to a temporary location
        temp_file_path = f'/tmp/{pdf_file.name}'
        with open(temp_file_path, 'wb+') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)

        try:
            # Use pdftotext to convert PDF to text
            result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True)
            if result.returncode != 0:
                return JsonResponse({'error': 'Conversion failed'}, status=500)

            # Return the converted text
            return HttpResponse(result.stdout, content_type='text/plain')
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return JsonResponse({'error': 'Invalid request method'}, status=400)