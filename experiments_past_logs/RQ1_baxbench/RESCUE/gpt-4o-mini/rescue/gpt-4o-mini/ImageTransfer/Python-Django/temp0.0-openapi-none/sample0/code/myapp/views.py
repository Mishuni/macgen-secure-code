from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import Image
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        image_url = fs.url(filename)
        image = Image.objects.create(image=image_url)
        return JsonResponse({'id': image.id}, status=200)
    return JsonResponse({'error': 'Bad request, invalid input'}, status=400)

def share_image(request, imageId):
    try:
        image = Image.objects.get(id=imageId)
        image_path = image.image.path
        with open(image_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='image/jpeg')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(image_path)
            return response
    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)