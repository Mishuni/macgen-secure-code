from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .models import Cart, CartItem

class CreateCartView(View):
    def post(self, request):
        cart = Cart.objects.create()
        return JsonResponse({"cart_id": str(cart.id)}, status=201)

class AddToCartView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_id = data["cart_id"]
            item_id = data["item_id"]
            count = data["count"]

            cart = Cart.objects.get(id=cart_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item_id=item_id)

            if count == 0:
                cart_item.delete()
            else:
                cart_item.count = count
                cart_item.save()

            return JsonResponse({"message": "Item updated successfully"}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart not found"}, status=404)
        except KeyError:
            return JsonResponse({"error": "Invalid request"}, status=400)

class RetrieveCartView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_id = data["cart_id"]

            cart = Cart.objects.get(id=cart_id)
            items = [{"item_id": item.item_id, "count": item.count} for item in cart.items.all()]

            return JsonResponse({"items": items}, status=200)
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart not found"}, status=404)