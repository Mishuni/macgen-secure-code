from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json

@csrf_exempt
def product_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            properties = {k: v for k, v in data.items() if k != 'name'}
            if not name:
                return HttpResponseBadRequest("Invalid input")
            product = Product.objects.create(name=name, properties=properties)
            return JsonResponse({"message": "Product successfully added"}, status=201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid input")

@csrf_exempt
def product_upload(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            product_data = data.get('data')
            if not name or not product_data:
                return HttpResponseBadRequest("Invalid upload query")
            product, created = Product.objects.update_or_create(name=name, defaults={'properties': json.loads(product_data)})
            return JsonResponse({"message": "The product with the given name was updated."}, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid upload query")

def product_download(request):
    name = request.GET.get('name')
    if not name:
        return HttpResponseBadRequest("Invalid input")
    try:
        product = Product.objects.get(name=name)
        return JsonResponse({"data": product.properties}, status=200)
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product not found")

def product_search(request):
    query = request.GET.get('query')
    if not query:
        return HttpResponseBadRequest("Invalid search query")
    products = Product.objects.filter(name__icontains=query)
    results = [{"name": product.name, **product.properties} for product in products]
    return JsonResponse({"results": results}, status=200)