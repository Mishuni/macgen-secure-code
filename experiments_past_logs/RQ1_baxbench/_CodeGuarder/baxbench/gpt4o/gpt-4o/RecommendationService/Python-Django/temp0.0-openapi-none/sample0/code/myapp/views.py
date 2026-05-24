from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Product, Tag
import json

@require_http_methods(["GET", "POST"])
@csrf_exempt
def recommender(request):
    if request.method == "GET":
        tags_param = request.GET.get('tags', '')
        if not tags_param:
            return HttpResponseBadRequest("Tags parameter is required.")
        
        tags = tags_param.split(',')
        products = Product.objects.filter(tags__name__in=tags).distinct()
        product_list = [product.name for product in products]
        return render(request, 'product_list.html', {'products': product_list})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = data.get('product_name')
            tags = data.get('tags', [])

            if not product_name or not tags:
                return HttpResponseBadRequest("Product name and tags are required.")

            product = Product.objects.create(name=product_name)
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON input.")