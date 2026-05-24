from django.test import TestCase

class CompilationTestCase(TestCase):
    def test_compile_endpoint(self):
        response = self.client.post('/compile', {
            'fileName': 'main.cpp',
            'fileContent': 'int main() { return 0; }'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('hasError', response.json())