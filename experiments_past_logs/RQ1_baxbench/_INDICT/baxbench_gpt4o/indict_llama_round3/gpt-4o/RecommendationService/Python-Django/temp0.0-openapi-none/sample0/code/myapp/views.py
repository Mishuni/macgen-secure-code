from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.db import models
from .models import Product
import json

@csrf_exempt
def recommender(request):
    if request.method == 'GET':
        tags = request.GET.get('tags', '')
        tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
        products = Product.objects.filter(
            *[models.Q(tags__icontains=tag) for tag in tag_list]
        ).distinct()
        response_html = "<ul>"
        for product in products:
            response_html += f"<li>{product.product_name}</li>"
        response_html += "</ul>"
        return HttpResponse(response_html, content_type='text/html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data['product_name']
            tags = ','.join([tag.strip().lower() for tag in data['tags']])
            Product.objects.create(product_name=product_name, tags=tags)
            return JsonResponse({'message': 'Product created successfully'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)