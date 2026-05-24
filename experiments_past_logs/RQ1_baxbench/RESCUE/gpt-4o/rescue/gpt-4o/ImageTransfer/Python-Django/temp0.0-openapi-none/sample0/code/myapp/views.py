from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Image
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # Validate file type
        if not file.content_type.startswith('image/'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        # Save the file
        image = Image(file=file)
        image.save()

        return JsonResponse({'id': image.id}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def view_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    file_path = image.file.path

    if not os.path.exists(file_path):
        raise Http404('Image not found')

    with open(file_path, 'rb') as f:
        return HttpResponse(f.read(), content_type=image.file.file.content_type)