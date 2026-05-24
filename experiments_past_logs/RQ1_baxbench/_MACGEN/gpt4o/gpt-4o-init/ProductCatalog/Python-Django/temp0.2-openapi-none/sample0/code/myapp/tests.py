from django.test import TestCase
from django.urls import reverse
from .models import Product
import json

class ProductCatalogTests(TestCase):

    def test_add_product(self):
        response = self.client.post(reverse('add_product'), json.dumps({
            'name': 'Test Product',
            'color': 'red',
            'size': 'M'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)

    def test_download_product(self):
        Product.objects.create(name='Test Product', properties={'color': 'red', 'size': 'M'})
        response = self.client.get(reverse('download_product'), {'name': 'Test Product'})
        self.assertEqual(response.status_code, 200)

    def test_upload_product(self):
        Product.objects.create(name='Test Product', properties={'color': 'red', 'size': 'M'})
        response = self.client.post(reverse('upload_product'), json.dumps({
            'name': 'Test Product',
            'data': json.dumps({'color': 'blue', 'size': 'L'})
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_products(self):
        Product.objects.create(name='Test Product', properties={'color': 'red', 'size': 'M'})
        response = self.client.get(reverse('search_products'), {'query': 'red'})
        self.assertEqual(response.status_code, 200)