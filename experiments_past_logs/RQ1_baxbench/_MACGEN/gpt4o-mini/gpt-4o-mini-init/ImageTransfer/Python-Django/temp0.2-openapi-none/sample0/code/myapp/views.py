from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import Image

class ImageUploadView(View):
    def post(self, request):
        file = request.FILES.get('file')
        if not file or not file.content_type.startswith('image/'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        image = Image.objects.create(file=file)
        return JsonResponse({'id': image.id}, status=200)

class ImageRetrieveView(View):
    def get(self, request, imageId):
        try:
            image = Image.objects.get(id=imageId)
            response = HttpResponse(image.file, content_type=image.file.file.content_type)
            response['Content-Disposition'] = 'inline; filename=' + image.file.name
            return response
        except Image.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)