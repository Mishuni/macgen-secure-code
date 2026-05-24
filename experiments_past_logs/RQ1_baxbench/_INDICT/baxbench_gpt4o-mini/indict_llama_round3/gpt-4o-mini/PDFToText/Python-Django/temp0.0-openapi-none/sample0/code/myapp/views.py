import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def convert_pdf_to_text(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        pdf_file = request.FILES['file']
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Invalid file type. Only PDF files are allowed.'}, status=400)

        # Save the file to a temporary location
        fs = FileSystemStorage(location='/tmp')
        filename = fs.save(pdf_file.name, pdf_file)
        pdf_file_path = os.path.join('/tmp', filename)

        try:
            # Use pdftotext to convert PDF to text
            text_output = subprocess.check_output(['pdftotext', pdf_file_path, '-'], stderr=subprocess.STDOUT)
            return HttpResponse(text_output, content_type='text/plain')
        except subprocess.CalledProcessError as e:
            return JsonResponse({'error': 'Conversion failed', 'details': e.output.decode()}, status=500)
        finally:
            # Clean up the temporary file
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)

    return JsonResponse({'error': 'Invalid request method'}, status=400)