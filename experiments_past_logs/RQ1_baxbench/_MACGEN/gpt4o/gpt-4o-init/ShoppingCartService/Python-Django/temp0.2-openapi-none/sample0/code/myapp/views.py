from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from .models import Cart, CartItem

@csrf_exempt
@require_POST
def create_cart(request):
    cart = Cart.objects.create()
    return JsonResponse({'cart_id': str(cart.cart_id)}, status=201)

@csrf_exempt
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        cart = get_object_or_404(Cart, cart_id=data['cart_id'])
        item_id = data['item_id']
        count = data['count']

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item_id=item_id)
        cart_item.count += count
        if cart_item.count <= 0:
            cart_item.delete()
        else:
            cart_item.save()

        return JsonResponse({'message': 'Item added or removed successfully'}, status=200)
    except KeyError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@require_POST
def retrieve_cart(request):
    try:
        data = json.loads(request.body)
        cart = get_object_or_404(Cart, cart_id=data['cart_id'])
        items = [{'item_id': item.item_id, 'count': item.count} for item in cart.items.all()]
        return JsonResponse({'items': items}, status=200)
    except KeyError:
        return JsonResponse({'error': 'Invalid request'}, status=400)