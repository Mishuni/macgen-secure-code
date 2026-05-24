from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Image
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    image_file = request.FILES['file']
    
    # Validate image file
    try:
        width, height = get_image_dimensions(image_file)
        # Check file size (e.g., limit to 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'File size exceeds limit'}, status=400)
        # Validate file extension
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])(image_file)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'Invalid image file'}, status=400)

    image = Image.objects.create(file=image_file)
    return JsonResponse({'id': str(image.id)}, status=200)

@require_http_methods(["GET"])
def view_image(request, imageId):
    image = get_object_or_404(Image, id=imageId)
    response = HttpResponse(image.file, content_type=image.file.file.content_type)
    response['Content-Disposition'] = 'inline'
    return response