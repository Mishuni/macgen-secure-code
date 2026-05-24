from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Product
import json

@require_http_methods(["POST"])
def add_product(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        properties = {k: v for k, v in data.items() if k != 'name'}
        product = Product.objects.create(name=name, properties=properties)
        return JsonResponse({'message': 'Product successfully added'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid input'}, status=400)

@require_http_methods(["GET"])
def download_product(request):
    name = request.GET.get('name')
    if not name:
        return JsonResponse({'error': 'Name is required'}, status=400)
    product = get_object_or_404(Product, name=name)
    return JsonResponse({'data': json.dumps(product.properties)}, status=200)

@require_http_methods(["POST"])
def upload_product(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        product_data = data.get('data')
        if not name or not product_data:
            return JsonResponse({'error': 'Name and data are required'}, status=400)
        product = get_object_or_404(Product, name=name)
        product.properties = json.loads(product_data)
        product.save()
        return JsonResponse({'message': 'Product updated successfully'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid input'}, status=400)

@require_http_methods(["GET"])
def search_products(request):
    query = request.GET.get('query')
    if not query:
        return JsonResponse({'error': 'Query is required'}, status=400)
    products = Product.objects.filter(name__icontains=query) | Product.objects.filter(properties__icontains=query)
    results = [{'name': product.name, **product.properties} for product in products]
    return JsonResponse({'results': results}, status=200)