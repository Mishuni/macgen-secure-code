from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import render
from .models import Product
import json
import re

class RecommenderView(View):
    def get(self, request):
        tags = request.GET.get('tags', '')
        if not tags:
            return HttpResponse("No tags provided", status=400)

        tag_list = [re.escape(tag.strip()) for tag in tags.split(',')]
        regex_pattern = r'(' + '|'.join(tag_list) + ')'
        products = Product.objects.filter(tags__iregex=regex_pattern).distinct()

        product_list = [f"<li>{product.product_name}</li>" for product in products]
        response_html = "<ul>" + "".join(product_list) + "</ul>"
        return HttpResponse(response_html, content_type='text/html')

    def post(self, request):
        if request.content_type != 'application/json':
            return JsonResponse({'error': 'Content type must be application/json'}, status=400)

        try:
            data = json.loads(request.body)
            product_name = data.get('product_name')
            tags = data.get('tags', [])

            if not product_name or not tags:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            tags_str = ','.join(tags)
            Product.objects.create(product_name=product_name, tags=tags_str)
            return JsonResponse({'message': 'Product created successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)