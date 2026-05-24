import os
import tempfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.files.uploadedfile import UploadedFile
from PyPDF2 import PdfReader, PdfWriter

@require_POST
def concatenate_pdfs(request):
    files = request.FILES.getlist('files')
    if not files or len(files) < 2:
        return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

    with tempfile.TemporaryDirectory() as temp_dir:
        input_file_paths = []

        try:
            for file in files:
                if not isinstance(file, UploadedFile) or not file.name.endswith('.pdf'):
                    return JsonResponse({'error': 'All files must be PDFs.'}, status=400)

                temp_file_path = os.path.join(temp_dir, file.name)
                with open(temp_file_path, 'wb') as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)

                # Validate PDF
                try:
                    PdfReader(temp_file_path)
                except Exception:
                    return JsonResponse({'error': 'Invalid PDF file.'}, status=400)

                input_file_paths.append(temp_file_path)

            output_file_path = os.path.join(temp_dir, 'concatenated.pdf')
            pdf_writer = PdfWriter()

            for pdf_path in input_file_paths:
                pdf_reader = PdfReader(pdf_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

            with open(output_file_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            with open(output_file_path, 'rb') as output_file:
                response = HttpResponse(output_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response

        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)