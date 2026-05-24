import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def convert_pdf_to_text(request):
    if request.method == 'POST':
        # Validate if a file is provided
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        pdf_file = request.FILES['file']

        # Validate file type
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Invalid file type. Only PDF files are allowed.'}, status=400)

        # Save the file temporarily
        try:
            file_path = default_storage.save(pdf_file.name, ContentFile(pdf_file.read()))
            full_path = os.path.join(default_storage.location, file_path)

            # Use pdftotext to extract text
            try:
                result = subprocess.run(
                    ['pdftotext', full_path, '-'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
                text_content = result.stdout
            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': 'Failed to convert PDF to text'}, status=500)
            finally:
                # Clean up the temporary file
                if os.path.exists(full_path):
                    os.remove(full_path)

            return HttpResponse(text_content, content_type='text/plain')

        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the file'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)