from django.http import JsonResponse
from django.views import View
from .models import Product
import json
from django.core.exceptions import ValidationError

class ProductView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not isinstance(name, str):
                raise ValidationError("Name must be a string.")
            properties = {k: v for k, v in data.items() if k != 'name'}
            product, created = Product.objects.update_or_create(name=name, defaults={'properties': properties})
            return JsonResponse({'message': 'Product successfully added'}, status=201 if created else 200)
        except (KeyError, json.JSONDecodeError, ValidationError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

    def get(self, request):
        query = request.GET.get('query', '')
        if query:
            products = Product.objects.filter(name__icontains=query)
            results = [{'name': product.name, **product.properties} for product in products]
            return JsonResponse({'results': results}, status=200)
        return JsonResponse({'error': 'Invalid search query'}, status=400)

class DownloadView(View):
    def get(self, request):
        name = request.GET.get('name')
        try:
            product = Product.objects.get(name=name)
            return JsonResponse({'data': json.dumps({'name': product.name, **product.properties})}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

class UploadView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            properties = data.get('data')
            if not isinstance(name, str) or not isinstance(properties, str):
                raise ValidationError("Invalid data format.")
            Product.objects.update_or_create(name=name, defaults={'properties': json.loads(properties)})
            return JsonResponse({'message': 'The product with the given name was updated.'}, status=200)
        except (KeyError, json.JSONDecodeError, ValidationError):
            return JsonResponse({'error': 'Invalid upload query'}, status=400)