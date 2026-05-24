import os
import uuid
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Image

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    file = request.FILES['file']
    image_id = str(uuid.uuid4())
    image_path = os.path.join('images', image_id + os.path.splitext(file.name)[1])
    path = default_storage.save(image_path, ContentFile(file.read()))

    Image.objects.create(id=image_id, file=path)

    return JsonResponse({'id': image_id}, status=200)

@require_http_methods(["GET"])
def view_image(request, image_id):
    try:
        image = Image.objects.get(id=image_id)
        image_path = os.path.join(settings.MEDIA_ROOT, image.file.name)
        if not os.path.exists(image_path):
            raise Http404

        return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)