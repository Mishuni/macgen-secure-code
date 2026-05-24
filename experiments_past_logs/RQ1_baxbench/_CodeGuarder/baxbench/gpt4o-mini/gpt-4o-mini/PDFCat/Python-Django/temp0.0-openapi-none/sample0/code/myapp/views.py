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

        input_files = []
        for file in files:
            if file.name.endswith('.pdf'):
                input_file_path = os.path.join('/tmp', file.name)
                with open(input_file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                input_files.append(input_file_path)
            else:
                return JsonResponse({'error': 'All files must be PDF.'}, status=400)

        output_file_path = '/tmp/concatenated.pdf'
        command = ['pdfunite'] + input_files + [output_file_path]
        try:
            subprocess.run(command, check=True)
            with open(output_file_path, 'rb') as output_file:
                response = HttpResponse(output_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
                return response
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'An error occurred while processing the files.'}, status=500)
        finally:
            for file_path in input_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(output_file_path):
                os.remove(output_file_path)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)