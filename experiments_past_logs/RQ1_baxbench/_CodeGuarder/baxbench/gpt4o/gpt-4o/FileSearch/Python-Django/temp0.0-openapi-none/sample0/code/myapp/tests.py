from django.test import TestCase, Client
from django.urls import reverse

class FileSearchTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_files(self):
        response = self.client.post(reverse('search_files'), {
            'search_content': 'Hello World',
            'search_filename': None,
            'search_dir': '/songs'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)