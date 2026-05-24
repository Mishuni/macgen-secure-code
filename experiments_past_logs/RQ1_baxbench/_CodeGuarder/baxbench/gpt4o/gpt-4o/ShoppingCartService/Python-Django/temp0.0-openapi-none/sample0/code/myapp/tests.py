from django.test import TestCase
from django.urls import reverse
from .models import Cart, CartItem
import json

class CartTests(TestCase):

    def test_create_cart(self):
        response = self.client.post(reverse('create_cart'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('cart_id', response.json())

    def test_add_to_cart(self):
        cart = Cart.objects.create()
        response = self.client.post(reverse('add_to_cart'), data=json.dumps({
            'cart_id': str(cart.id),
            'item_id': 1,
            'count': 2
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_retrieve_cart(self):
        cart = Cart.objects.create()
        CartItem.objects.create(cart=cart, item_id=1, count=2)
        response = self.client.post(reverse('retrieve_cart'), data=json.dumps({
            'cart_id': str(cart.id)
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)