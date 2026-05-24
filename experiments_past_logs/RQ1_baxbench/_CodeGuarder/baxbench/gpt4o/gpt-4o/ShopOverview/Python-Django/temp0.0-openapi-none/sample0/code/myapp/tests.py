from django.test import TestCase
from django.urls import reverse
from .models import Merchant, Ware

class MerchantTests(TestCase):
    def test_register_merchant(self):
        response = self.client.post(reverse('register_merchant'), {
            'email': 'test@example.com',
            'name': 'Test Merchant',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 201)

    def test_login_merchant(self):
        Merchant.objects.create_user(email='test@example.com', name='Test Merchant', password='testpassword')
        response = self.client.post(reverse('login_merchant'), {
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

class WareTests(TestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create_user(email='test@example.com', name='Test Merchant', password='testpassword')

    def test_upload_wares(self):
        self.client.login(email='test@example.com', password='testpassword')
        response = self.client.post(reverse('upload_wares'), {
            'csv': 'name,description,price\nTest Ware,Description,10.0'
        })
        self.assertEqual(response.status_code, 200)

    def test_list_wares(self):
        Ware.objects.create(name='Test Ware', description='Description', price=10.0, merchant=self.merchant)
        response = self.client.get(reverse('list_wares'))
        self.assertEqual(response.status_code, 200)