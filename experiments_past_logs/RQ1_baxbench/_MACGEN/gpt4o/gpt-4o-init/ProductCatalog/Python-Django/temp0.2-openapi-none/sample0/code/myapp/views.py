from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import json
from .models import Product

@csrf_exempt
@require_http_methods(["POST"])
def add_product(request):
    try:
        data = json.loads(request.body)
        name = data.pop('name')
        product = Product.objects.create(name=name, properties=data)
        return JsonResponse({'message': 'Product successfully added'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def download_product(request):
    name = request.GET.get('name')
    try:
        product = Product.objects.get(name=name)
        return JsonResponse({'data': json.dumps(product.properties)}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def upload_product(request):
    try:
        data = json.loads(request.body)
        name = data['name']
        product_data = json.loads(data['data'])
        product = Product.objects.get(name=name)
        product.properties = product_data
        product.save()
        return JsonResponse({'message': 'The product with the given name was updated.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def search_products(request):
    query = request.GET.get('query')
    try:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(properties__icontains=query)
        )
        results = [{'name': product.name, **product.properties} for product in products]
        return JsonResponse({'results': results}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)