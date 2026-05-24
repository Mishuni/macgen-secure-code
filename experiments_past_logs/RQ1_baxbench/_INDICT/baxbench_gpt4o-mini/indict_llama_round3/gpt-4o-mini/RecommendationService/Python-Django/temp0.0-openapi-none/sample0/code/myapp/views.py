from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import Product
from django.db.models import Q
import json
from django.utils.html import escape

class RecommenderView(View):
    def get(self, request):
        tags = request.GET.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if not tag_list:
            return HttpResponse('<ul></ul>', content_type='text/html')

        query = Q()
        for tag in tag_list:
            query |= Q(tags__contains=[tag])  # Adjusted to use Q objects for better query handling

        products = Product.objects.filter(query)
        response_html = '<ul>' + ''.join(f'<li>{escape(product.product_name)}</li>' for product in products) + '</ul>'
        return HttpResponse(response_html, content_type='text/html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            product_name = data['product_name']
            tags = data['tags']
            product = Product.objects.create(product_name=product_name, tags=tags)
            return JsonResponse({'message': 'Product created successfully'}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)