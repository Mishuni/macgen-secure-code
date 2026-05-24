from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
import json

@csrf_exempt
def create_cart(request):
    if request.method == 'POST':
        cart = Cart.objects.create(cart_id='cart_' + str(Cart.objects.count() + 1))
        return JsonResponse({'cart_id': cart.cart_id}, status=201)

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        item_id = data.get('item_id')
        count = data.get('count')

        if not isinstance(cart_id, str) or not isinstance(item_id, int) or not isinstance(count, int):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        try:
            cart = Cart.objects.get(cart_id=cart_id)
            if count < 0:
                CartItem.objects.filter(cart=cart, item_id=item_id).delete()
            else:
                CartItem.objects.update_or_create(cart=cart, item_id=item_id, defaults={'count': count})
            return JsonResponse({'message': 'Item added or removed successfully'}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)

@csrf_exempt
def retrieve_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')

        if not isinstance(cart_id, str):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        try:
            cart = Cart.objects.get(cart_id=cart_id)
            items = [{'item_id': item.item_id, 'count': item.count} for item in cart.items.all()]
            return JsonResponse({'items': items}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)