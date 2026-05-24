import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from .models import Product

class ProductCatalogView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not name:
                return HttpResponseBadRequest(json.dumps({'error': 'Invalid input'}), content_type='application/json')

            properties = {k: v for k, v in data.items() if k != 'name'}
            product, created = Product.objects.update_or_create(name=name, defaults={'properties': properties})

            return JsonResponse({'message': 'Product successfully added'}, status=201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid input'}), content_type='application/json')

    def get(self, request):
        name = request.GET.get('name')
        if not name:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid input'}), content_type='application/json')

        try:
            product = Product.objects.get(name=name)
            return JsonResponse({'data': product.properties}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'data': {}}, status=200)

class ProductUploadView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            product_data = data.get('data')

            if not name or not product_data:
                return HttpResponseBadRequest(json.dumps({'error': 'Invalid upload query'}), content_type='application/json')

            Product.objects.update_or_create(name=name, defaults={'properties': json.loads(product_data)})
            return JsonResponse({'message': 'Product updated'}, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid upload query'}), content_type='application/json')

class ProductSearchView(View):
    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid search query'}), content_type='application/json')

        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(properties__contains=query)
        results = [{'name': product.name, **product.properties} for product in products]
        return JsonResponse({'results': results}, status=200)