from django.test import TestCase
from django.urls import reverse
from .models import Click
from datetime import datetime

class ClickTests(TestCase):

    def test_register_click(self):
        response = self.client.post(reverse('register_click'))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Click.objects.count(), 1)

    def test_retrieve_clicks(self):
        click = Click.objects.create()
        date_str = click.timestamp.strftime('%Y-%m-%d')
        response = self.client.get(reverse('retrieve_clicks'), {'date': date_str, 'direction': '>='})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)