from django.test import TestCase
from django.urls import reverse
from .models import Click
from datetime import datetime

class ClickTests(TestCase):
    def test_register_click(self):
        response = self.client.post(reverse('register_click'), {})
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('register_click'), {'timestamp': datetime.now().isoformat()})
        self.assertEqual(response.status_code, 201)

    def test_retrieve_clicks(self):
        Click.objects.create(timestamp=datetime.now())
        response = self.client.get(reverse('retrieve_clicks'), {'date': '2022-01-01', 'direction': '>'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id')