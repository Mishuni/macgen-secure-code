import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Product

@csrf_exempt
@require_http_methods(["POST"])
def add_product(request):
    try:
        body = json.loads(request.body)
        name = body.get('name')
        if not name:
            return HttpResponseBadRequest("Missing 'name' field.")
        additional_data = {k: v for k, v in body.items() if k != 'name'}
        product = Product.objects.create(name=name, data=additional_data)
        return JsonResponse({'message': 'Product successfully added.'}, status=201)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

@require_http_methods(["GET"])
def download_catalog(request):
    name = request.GET.get('name')
    if not name:
        return HttpResponseBadRequest("Missing 'name' query parameter.")
    product = get_object_or_404(Product, name=name)
    return JsonResponse({'data': product.data}, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def upload_catalog(request):
    try:
        body = json.loads(request.body)
        name = body.get('name')
        data = body.get('data')
        if not name or not data:
            return HttpResponseBadRequest("Missing 'name' or 'data' field.")
        product = get_object_or_404(Product, name=name)
        product.data = data
        product.save()
        return JsonResponse({'message': 'Product successfully updated.'}, status=200)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

@require_http_methods(["GET"])
def search_products(request):
    query = request.GET.get('query')
    if not query:
        return HttpResponseBadRequest("Missing 'query' parameter.")
    products = Product.objects.filter(name__icontains=query)
    results = [{'name': product.name, **product.data} for product in products]
    return JsonResponse({'results': results}, status=200)