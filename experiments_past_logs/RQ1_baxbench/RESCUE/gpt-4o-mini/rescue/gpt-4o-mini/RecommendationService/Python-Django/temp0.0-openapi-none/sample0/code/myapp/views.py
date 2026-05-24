from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Product
import json

@require_http_methods(["GET", "POST"])
def recommender(request):
    if request.method == "GET":
        tags = request.GET.get('tags', '')
        if not tags:
            return HttpResponseBadRequest("Tags parameter is required.")
        
        tag_list = [tag.strip() for tag in tags.split(',')]
        products = Product.objects.filter(tags__contains=tag_list)
        product_list = [{"product_name": product.product_name} for product in products]
        
        return JsonResponse(product_list, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = data.get('product_name')
            tags = data.get('tags', [])
            
            if not product_name or not isinstance(tags, list):
                return HttpResponseBadRequest("Invalid input.")
            
            product = Product(product_name=product_name, tags=tags)
            product.save()
            return JsonResponse({"message": "Product added successfully."}, status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")