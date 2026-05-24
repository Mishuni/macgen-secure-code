from django.test import TestCase
from django.urls import reverse
from .models import Merchant, Ware

class MerchantTests(TestCase):
    def test_register_merchant(self):
        response = self.client.post(reverse('register_merchant'), {
            'email': 'test@example.com',
            'name': 'Test Merchant',
            'password': 'password123'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_login_merchant(self):
        Merchant.objects.create_user(email='test@example.com', name='Test Merchant', password='password123')
        response = self.client.post(reverse('login_merchant'), {
            'email': 'test@example.com',
            'password': 'password123'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)

class WareTests(TestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create_user(email='test@example.com', name='Test Merchant', password='password123')

    def test_upload_wares(self):
        self.client.login(email='test@example.com', password='password123')
        csv_data = "name,description,price\nItem1,Description1,10.0\nItem2,Description2,20.0"
        response = self.client.post(reverse('upload_wares'), {'csv': csv_data}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_list_wares(self):
        Ware.objects.create(name='Item1', description='Description1', price=10.0, merchant=self.merchant)
        response = self.client.get(reverse('list_wares'))
        self.assertEqual(response.status_code, 200)