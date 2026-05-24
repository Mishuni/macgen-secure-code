from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(name="Test Product", data={"key": "value"})
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.data, {"key": "value"})