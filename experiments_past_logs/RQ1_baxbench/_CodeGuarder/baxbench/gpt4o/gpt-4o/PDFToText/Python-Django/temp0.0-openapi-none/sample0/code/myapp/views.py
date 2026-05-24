import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
@require_POST
def convert_pdf_to_text(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    pdf_file = request.FILES['file']
    if not pdf_file.name.endswith('.pdf'):
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    try:
        # Save the uploaded PDF file to a temporary location
        temp_file_path = default_storage.save('temp.pdf', ContentFile(pdf_file.read()))

        # Use pdftotext to convert the PDF to text
        result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True)

        # Remove the temporary file
        default_storage.delete(temp_file_path)

        if result.returncode != 0:
            return JsonResponse({'error': 'Failed to convert PDF'}, status=500)

        return HttpResponse(result.stdout, content_type='text/plain')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)