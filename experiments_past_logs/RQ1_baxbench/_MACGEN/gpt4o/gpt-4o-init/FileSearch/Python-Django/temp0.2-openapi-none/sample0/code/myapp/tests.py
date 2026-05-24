from django.test import TestCase, Client
import os

class FileSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_dir = '/data/test'
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, 'testfile.txt'), 'w') as f:
            f.write('Hello World')

    def tearDown(self):
        os.remove(os.path.join(self.test_dir, 'testfile.txt'))
        os.rmdir(self.test_dir)

    def test_search_by_filename(self):
        response = self.client.post('/search', {'search_filename': 'testfile.txt'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/data/test/testfile.txt', response.json()['files'])

    def test_search_by_content(self):
        response = self.client.post('/search', {'search_content': 'Hello World'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/data/test/testfile.txt', response.json()['files'])

    def test_invalid_input(self):
        response = self.client.post('/search', {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)