import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def convert_pdf(request):
    if request.method == 'POST' and request.FILES.get('file'):
        pdf_file = request.FILES['file']
        try:
            # Save the uploaded PDF file temporarily
            with open('temp.pdf', 'wb+') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Use pdftotext to convert PDF to text
            result = subprocess.run(['pdftotext', 'temp.pdf', '-'], capture_output=True, text=True)
            if result.returncode != 0:
                return JsonResponse({'error': 'Conversion failed'}, status=500)

            return JsonResponse(result.stdout, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid input or missing file'}, status=400)