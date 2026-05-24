from django.test import TestCase
from .models import Merchant, Ware

class MerchantTestCase(TestCase):
    def setUp(self):
        Merchant.objects.create(email="test@example.com", name="Test Merchant", password="password123")

    def test_merchant_creation(self):
        merchant = Merchant.objects.get(email="test@example.com")
        self.assertEqual(merchant.name, "Test Merchant")