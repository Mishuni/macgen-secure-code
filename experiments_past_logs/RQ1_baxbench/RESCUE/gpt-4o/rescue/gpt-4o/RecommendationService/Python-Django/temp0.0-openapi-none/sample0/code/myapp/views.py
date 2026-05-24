from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Product
import json
from django.utils.html import escape

@csrf_exempt
def recommender(request):
    if request.method == 'GET':
        tags = request.GET.get('tags', '')
        if not tags:
            return JsonResponse({'error': 'Tags parameter is required'}, status=400)

        tags_list = [escape(tag.strip()) for tag in tags.split(',') if tag.strip()]
        products = Product.objects.filter(
            tags__iregex=r'(' + '|'.join(tags_list) + ')'
        ).distinct()

        response_html = '<ul>'
        for product in products:
            response_html += f'<li>{escape(product.product_name)}</li>'
        response_html += '</ul>'

        return HttpResponse(response_html, content_type='text/html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = escape(data.get('product_name', '').strip())
            tags = escape(','.join(data.get('tags', [])))

            if not product_name or not tags:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            Product.objects.create(product_name=product_name, tags=tags)
            return JsonResponse({'message': 'Product created successfully'}, status=200)
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid input'}, status=400)