from django.test import TestCase
from django.urls import reverse
from .models import Product, Tag

class RecommenderTests(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="electronics")
        self.tag2 = Tag.objects.create(name="books")
        self.product1 = Product.objects.create(name="Laptop")
        self.product1.tags.add(self.tag1)
        self.product2 = Product.objects.create(name="Novel")
        self.product2.tags.add(self.tag2)

    def test_get_recommendations(self):
        response = self.client.get(reverse('recommender'), {'tags': 'electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laptop")

    def test_post_product(self):
        response = self.client.post(reverse('recommender'), 
                                    data={'product_name': 'Smartphone', 'tags': ['electronics']},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Product.objects.filter(name='Smartphone').exists())