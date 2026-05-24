from django.test import TestCase, Client
from django.urls import reverse
import json

class FileSearchTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_files_no_input(self):
        response = self.client.post(reverse('search_files'), data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_search_files_with_filename(self):
        response = self.client.post(reverse('search_files'), data=json.dumps({'search_filename': 'file.txt'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('files', response.json())

    def test_search_files_with_content(self):
        response = self.client.post(reverse('search_files'), data=json.dumps({'search_content': 'Hello World'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('files', response.json())