from django.test import TestCase
from .models import Click

class ClickModelTest(TestCase):
    def test_click_creation(self):
        click = Click.objects.create()
        self.assertIsNotNone(click.id)
        self.assertIsNotNone(click.timestamp)