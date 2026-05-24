from django.test import TestCase, Client
from django.urls import reverse
import json

class CompileCodeTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('compile_code')

    def test_compile_cpp_success(self):
        response = self.client.post(self.url, json.dumps({
            'fileName': 'main.cpp',
            'fileContent': 'int main() { return 0; }'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'hasError': False, 'compilerError': None})

    def test_compile_cpp_failure(self):
        response = self.client.post(self.url, json.dumps({
            'fileName': 'main.cpp',
            'fileContent': 'int main() { return; }'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['hasError'])

    def test_compile_ts_success(self):
        response = self.client.post(self.url, json.dumps({
            'fileName': 'main.ts',
            'fileContent': 'let x: number = 5;'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'hasError': False, 'compilerError': None})

    def test_compile_ts_failure(self):
        response = self.client.post(self.url, json.dumps({
            'fileName': 'main.ts',
            'fileContent': 'let x = y * 2;'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['hasError'])

    def test_invalid_file_type(self):
        response = self.client.post(self.url, json.dumps({
            'fileName': 'main.py',
            'fileContent': 'print("Hello, World!")'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json()['hasError'])

    def test_invalid_request_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)