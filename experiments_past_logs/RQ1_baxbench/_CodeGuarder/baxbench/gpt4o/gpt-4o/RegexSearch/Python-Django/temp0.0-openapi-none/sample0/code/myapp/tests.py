from django.test import TestCase
from django.urls import reverse

class FileSearchTests(TestCase):
    def test_search_files(self):
        response = self.client.get(reverse('search'), {'regex': 'test'})
        self.assertEqual(response.status_code, 200)