from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Product, Tag
import json

class RecommenderView(View):
    def get(self, request):
        tags_param = request.GET.get('tags', '')
        tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
        products = Product.objects.filter(tags__name__in=tags_list).distinct()
        response_html = "<ul>"
        for product in products:
            response_html += f"<li>{product.product_name}</li>"
        response_html += "</ul>"
        return HttpResponse(response_html, content_type='text/html')

    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_name = data.get('product_name')
            tags = data.get('tags', [])
            if not product_name or not isinstance(tags, list):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            product = Product.objects.create(product_name=product_name)
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)
            product.save()
            return JsonResponse({'message': 'Product added successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid input'}, status=400)