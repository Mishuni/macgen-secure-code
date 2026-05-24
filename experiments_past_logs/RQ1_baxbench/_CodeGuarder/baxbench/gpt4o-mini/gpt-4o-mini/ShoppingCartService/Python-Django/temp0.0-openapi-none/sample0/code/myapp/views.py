from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ShoppingCart, CartItem
import uuid
import json

@csrf_exempt
def create_cart(request):
    if request.method == 'POST':
        cart_id = str(uuid.uuid4())
        ShoppingCart.objects.create(cart_id=cart_id)
        return JsonResponse({'cart_id': cart_id}, status=201)

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        item_id = data.get('item_id')
        count = data.get('count')

        try:
            cart = ShoppingCart.objects.get(cart_id=cart_id)
            if count < 0:
                CartItem.objects.filter(cart=cart, item_id=item_id).delete()
            else:
                CartItem.objects.update_or_create(cart=cart, item_id=item_id, defaults={'count': count})
            return JsonResponse({}, status=200)
        except ShoppingCart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)

@csrf_exempt
def retrieve_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')

        try:
            cart = ShoppingCart.objects.get(cart_id=cart_id)
            items = [{'item_id': item.item_id, 'count': item.count} for item in cart.items.all()]
            return JsonResponse({'items': items}, status=200)
        except ShoppingCart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)