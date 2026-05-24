import os
import subprocess
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from tempfile import NamedTemporaryFile

@csrf_exempt
def concatenate_pdfs(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    # Validate input
    files = request.FILES.getlist('files')
    if not files or len(files) < 2:
        return JsonResponse({'error': 'At least two PDF files are required.'}, status=400)

    # Ensure all uploaded files are PDFs
    for file in files:
        if not file.name.endswith('.pdf'):
            return JsonResponse({'error': f'Invalid file type: {file.name}. Only PDF files are allowed.'}, status=400)

    # Create temporary files for processing
    temp_files = []
    try:
        for file in files:
            temp_file = NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(file.read())
            temp_file.close()
            temp_files.append(temp_file.name)

        # Output file
        output_file = NamedTemporaryFile(delete=False, suffix='.pdf')
        output_file.close()

        # Concatenate PDFs using pdfunite
        command = ['pdfunite'] + temp_files + [output_file.name]
        subprocess.run(command, check=True)

        # Return the concatenated PDF as a response
        response = FileResponse(open(output_file.name, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
        return response

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'An error occurred while concatenating the PDF files.'}, status=500)

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(output_file.name):
            os.remove(output_file.name)