from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Image
import mimetypes

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file = request.FILES['file']
        # Validate file type
        if not file.content_type.startswith('image/'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        image = Image.objects.create(image=file)
        return JsonResponse({'id': image.id}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def share_image(request, imageId):
    try:
        image = Image.objects.get(id=imageId)
        content_type, _ = mimetypes.guess_type(image.image.name)
        response = HttpResponse(image.image, content_type=content_type)
        response['Content-Disposition'] = 'inline; filename=' + image.image.name
        return response
    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)