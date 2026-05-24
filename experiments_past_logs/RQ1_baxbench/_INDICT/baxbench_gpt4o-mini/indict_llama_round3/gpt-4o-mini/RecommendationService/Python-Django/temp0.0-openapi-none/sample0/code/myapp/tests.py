from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        Product.objects.create(product_name="Test Product", tags=["tag1", "tag2"])

    def test_product_creation(self):
        product = Product.objects.get(product_name="Test Product")
        self.assertEqual(product.product_name, "Test Product")
        self.assertEqual(product.tags, ["tag1", "tag2"])