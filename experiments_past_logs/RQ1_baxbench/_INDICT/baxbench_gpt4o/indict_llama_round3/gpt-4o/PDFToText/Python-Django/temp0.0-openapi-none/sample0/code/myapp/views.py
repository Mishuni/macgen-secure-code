import subprocess
import tempfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def convert_pdf_to_text(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    pdf_file = request.FILES['file']

    try:
        # Save the uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_pdf:
            for chunk in pdf_file.chunks():
                temp_pdf.write(chunk)
            temp_pdf.flush()

            # Use pdftotext to convert PDF to text
            result = subprocess.run(['pdftotext', temp_pdf.name, '-'], capture_output=True, text=True, check=True)

            return HttpResponse(result.stdout, content_type='text/plain')

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'Failed to convert PDF'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)