import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views import View
from tempfile import NamedTemporaryFile, TemporaryDirectory

class PDFConcatenateView(View):
    def post(self, request):
        if 'files' not in request.FILES:
            return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

        pdf_files = request.FILES.getlist('files')
        if not pdf_files:
            return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

        # Validate file types
        for pdf_file in pdf_files:
            if not pdf_file.name.lower().endswith('.pdf'):
                return JsonResponse({'error': 'Only PDF files are allowed.'}, status=400)

        # Use a temporary directory to store files
        with TemporaryDirectory() as temp_dir:
            temp_files = []
            try:
                for pdf_file in pdf_files:
                    temp_file_path = os.path.join(temp_dir, pdf_file.name)
                    with open(temp_file_path, 'wb+') as temp_file:
                        for chunk in pdf_file.chunks():
                            temp_file.write(chunk)
                        temp_files.append(temp_file_path)

                # Define the output file path
                output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

                # Use pdfunite to concatenate the PDF files
                subprocess.run(['pdfunite'] + temp_files + [output_file_path], check=True)

                # Return the concatenated PDF
                with open(output_file_path, 'rb') as output_file:
                    response = HttpResponse(output_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                    return response

            except subprocess.CalledProcessError:
                return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)