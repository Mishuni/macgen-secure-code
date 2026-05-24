from django.test import TestCase, Client
from django.urls import reverse

class CompileViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_compile_typescript_success(self):
        response = self.client.post(reverse('compile'), data={
            'fileName': 'main.ts',
            'fileContent': 'let x = 2 * 15;'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'hasError': False, 'compilerError': None})

    def test_compile_cpp_success(self):
        response = self.client.post(reverse('compile'), data={
            'fileName': 'main.cpp',
            'fileContent': 'int main() { return 0; }'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'hasError': False, 'compilerError': None})

    def test_compile_with_error(self):
        response = self.client.post(reverse('compile'), data={
            'fileName': 'main.ts',
            'fileContent': 'let x = y * 2;'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['hasError'])
        self.assertIn('error TS2304', response.json()['compilerError'])

    def test_invalid_json(self):
        response = self.client.post(reverse('compile'), data='invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid JSON'})

    def test_unsupported_file_type(self):
        response = self.client.post(reverse('compile'), data={
            'fileName': 'main.py',
            'fileContent': 'print("Hello, World!")'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Unsupported file type'})