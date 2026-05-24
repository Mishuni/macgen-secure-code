from django.test import TestCase

class FileSearchTests(TestCase):
    def test_search_endpoint(self):
        response = self.client.post('/search/', {
            'search_content': 'Hello World',
            'search_filename': 'file.txt',
            'search_dir': '/songs'
        })
        self.assertEqual(response.status_code, 200)