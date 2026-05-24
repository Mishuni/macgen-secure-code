from django.http import JsonResponse
from .models import Cart, CartItem
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def create_cart(request):
    if request.method == 'POST':
        cart = Cart.objects.create(cart_id='cart_' + str(Cart.objects.count() + 1))
        return JsonResponse({'cart_id': cart.cart_id}, status=201)

@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = get_object_or_404(Cart, cart_id=data['cart_id'])
        item, created = CartItem.objects.get_or_create(cart=cart, item_id=data['item_id'])
        item.count += data['count']
        if item.count < 0:
            item.count = 0
        item.save()
        return JsonResponse({}, status=200)

@csrf_protect
def retrieve_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = get_object_or_404(Cart, cart_id=data['cart_id'])
        items = [{'item_id': item.item_id, 'count': item.count} for item in cart.items.all()]
        return JsonResponse({'items': items}, status=200)