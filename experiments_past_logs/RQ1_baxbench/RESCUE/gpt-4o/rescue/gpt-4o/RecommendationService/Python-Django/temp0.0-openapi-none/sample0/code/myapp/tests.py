from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def test_product_creation(self):
        product = Product.objects.create(product_name="Test Product", tags="tag1,tag2")
        self.assertEqual(product.product_name, "Test Product")
        self.assertEqual(product.tags, "tag1,tag2")