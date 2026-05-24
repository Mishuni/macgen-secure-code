from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        Product.objects.create(name="Test Product", properties={"color": "red", "size": "M"})

    def test_product_creation(self):
        product = Product.objects.get(name="Test Product")
        self.assertEqual(product.properties['color'], "red")
        self.assertEqual(product.properties['size'], "M")