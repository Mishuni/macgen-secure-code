from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Image
from django.core.files.storage import FileSystemStorage
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)
        image = Image(file=filename)
        image.save()
        return JsonResponse({'id': image.id}, status=200)
    return JsonResponse({'error': 'Invalid input'}, status=400)

def share_image(request, imageId):
    try:
        image = Image.objects.get(id=imageId)
        file_path = image.file.path
        with open(file_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='image/jpeg')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)