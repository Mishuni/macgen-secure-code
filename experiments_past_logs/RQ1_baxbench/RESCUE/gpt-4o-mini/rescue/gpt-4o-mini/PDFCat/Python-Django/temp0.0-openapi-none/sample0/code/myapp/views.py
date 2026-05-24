import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def concatenate_pdfs(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        
        if not files:
            return JsonResponse({'error': 'Invalid input or missing files.'}, status=400)

        # Validate that all uploaded files are PDFs
        for file in files:
            if not file.name.endswith('.pdf'):
                return JsonResponse({'error': 'All files must be PDF format.'}, status=400)

        # Create a temporary directory to store the uploaded files
        temp_dir = 'temp_pdfs'
        os.makedirs(temp_dir, exist_ok=True)

        pdf_file_paths = []
        try:
            for file in files:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                pdf_file_paths.append(file_path)

            # Define the output file path
            output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

            # Use pdfunite to concatenate the PDFs
            subprocess.run(['pdfunite'] + pdf_file_paths + [output_file_path], check=True)

            # Serve the concatenated PDF
            with open(output_file_path, 'rb') as output_file:
                response = HttpResponse(output_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response

        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)

        finally:
            # Clean up temporary files
            for file_path in pdf_file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
            os.rmdir(temp_dir)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)