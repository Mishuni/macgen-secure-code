from django.test import TestCase
from .models import Cart, CartItem

class CartTestCase(TestCase):
    def test_create_cart(self):
        cart = Cart.objects.create()
        self.assertIsNotNone(cart.id)

    def test_add_to_cart(self):
        cart = Cart.objects.create()
        CartItem.objects.create(cart=cart, item_id=1, count=2)
        self.assertEqual(cart.items.count(), 1)

    def test_retrieve_cart(self):
        cart = Cart.objects.create()
        CartItem.objects.create(cart=cart, item_id=1, count=2)
        items = list(cart.items.all())
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].item_id, 1)
        self.assertEqual(items[0].count, 2)