from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json
import re

@csrf_exempt
def recommender(request):
    allowed_tags = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")

    if request.method == 'GET':
        tags = request.GET.get('tags', '').split(',')
        if not all(tag in allowed_tags for tag in tags):
            return JsonResponse({'error': 'Invalid input tag'}, status=400)

        products = Product.objects.filter(tags__overlap=tags)
        response_html = '<ul>' + ''.join(f'<li>{product.product_name}</li>' for product in products) + '</ul>'
        return HttpResponse(response_html, content_type='text/html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data['product_name']
            tags = data['tags']

            if not isinstance(product_name, str) or not all(tag in allowed_tags for tag in tags):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            product = Product(product_name=product_name, tags=tags)
            product.save()
            return JsonResponse({'message': 'Product added successfully'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)