from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from .models import Image
import os
from PIL import Image as PILImage

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # Validate image format
        try:
            img = PILImage.open(file)
            if img.format not in settings.PILLOW_FORMATS_QUESTIONS_IMAGE:
                return JsonResponse({'error': 'Unsupported image format'}, status=400)
        except Exception:
            return JsonResponse({'error': 'Invalid image file'}, status=400)

        # Save the image
        image_instance = Image(file=file)
        image_instance.save()

        return JsonResponse({'id': image_instance.id}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def view_image(request, imageId):
    image = get_object_or_404(Image, id=imageId)
    file_path = image.file.path
    if not os.path.exists(file_path):
        raise Http404("Image not found")

    with open(file_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/jpeg')