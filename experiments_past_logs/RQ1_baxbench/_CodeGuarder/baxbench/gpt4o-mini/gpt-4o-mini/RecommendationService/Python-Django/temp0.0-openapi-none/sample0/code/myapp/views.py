from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json

@csrf_exempt
def recommender(request):
    if request.method == 'GET':
        tags = request.GET.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        products = Product.objects.filter(tags__name__in=tag_list).distinct()
        response_html = '<ul>' + ''.join(f'<li>{product.product_name}</li>' for product in products) + '</ul>'
        return HttpResponse(response_html, content_type='text/html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('product_name')
            tags = data.get('tags', [])
            if not product_name or not isinstance(tags, list):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            product = Product.objects.create(product_name=product_name)
            product.tags.set(*tags)
            return JsonResponse({'message': 'Product created successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)