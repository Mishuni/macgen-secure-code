from django.test import TestCase
from django.urls import reverse
from .models import Product, Tag
import json

class RecommenderViewTests(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name='electronics')
        self.tag2 = Tag.objects.create(name='books')
        self.product1 = Product.objects.create(product_name='Laptop')
        self.product1.tags.add(self.tag1)
        self.product2 = Product.objects.create(product_name='Novel')
        self.product2.tags.add(self.tag2)

    def test_get_recommendations(self):
        response = self.client.get(reverse('recommender'), {'tags': 'electronics'})
        self.assertContains(response, 'Laptop')
        self.assertNotContains(response, 'Novel')

    def test_post_product(self):
        response = self.client.post(reverse('recommender'), data=json.dumps({
            'product_name': 'Smartphone',
            'tags': ['electronics', 'gadgets']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Product.objects.filter(product_name='Smartphone').exists())