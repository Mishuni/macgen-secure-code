from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
import json
import uuid

@csrf_exempt
def create_cart(request):
    if request.method == 'POST':
        cart_id = str(uuid.uuid4())
        Cart.objects.create(cart_id=cart_id)
        return JsonResponse({'cart_id': cart_id}, status=201)

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        item_id = data.get('item_id')
        count = data.get('count')

        try:
            cart = Cart.objects.get(cart_id=cart_id)
            if count < 0:
                cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
                if cart_item.count + count <= 0:
                    cart_item.delete()
                else:
                    cart_item.count += count
                    cart_item.save()
            else:
                cart_item, created = CartItem.objects.get_or_create(cart=cart, item_id=item_id)
                cart_item.count += count
                cart_item.save()
            return JsonResponse({}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)

@csrf_exempt
def retrieve_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')

        try:
            cart = Cart.objects.get(cart_id=cart_id)
            items = [{'item_id': item.item_id, 'count': item.count} for item in cart.items.all()]
            return JsonResponse({'items': items}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found'}, status=404)