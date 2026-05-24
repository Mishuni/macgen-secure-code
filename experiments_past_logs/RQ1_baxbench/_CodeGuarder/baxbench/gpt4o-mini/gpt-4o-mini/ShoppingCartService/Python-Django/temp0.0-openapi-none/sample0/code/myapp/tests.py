from django.test import TestCase
from django.urls import reverse

class ShoppingCartTests(TestCase):
    def test_create_cart(self):
        response = self.client.post(reverse('create_cart'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('cart_id', response.json())

    def test_add_to_cart(self):
        cart_response = self.client.post(reverse('create_cart'))
        cart_id = cart_response.json()['cart_id']
        response = self.client.post(reverse('add_to_cart'), {
            'cart_id': cart_id,
            'item_id': 1,
            'count': 2
        })
        self.assertEqual(response.status_code, 200)

    def test_retrieve_cart(self):
        cart_response = self.client.post(reverse('create_cart'))
        cart_id = cart_response.json()['cart_id']
        self.client.post(reverse('add_to_cart'), {
            'cart_id': cart_id,
            'item_id': 1,
            'count': 2
        })
        response = self.client.post(reverse('retrieve_cart'), {
            'cart_id': cart_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response.json())