import os
import subprocess
import tempfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def concatenate_pdfs(request):
    files = request.FILES.getlist('files')
    
    if not files or len(files) < 2:
        return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

    input_filenames = []
    try:
        for file in files:
            # Use a secure temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_file.write(file.read())
            temp_file.close()
            input_filenames.append(temp_file.name)

        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_filename = output_file.name
        output_file.close()

        try:
            subprocess.run(['pdfunite'] + input_filenames + [output_filename], check=True)
            with open(output_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)
    finally:
        for filename in input_filenames:
            if os.path.exists(filename):
                os.remove(filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)