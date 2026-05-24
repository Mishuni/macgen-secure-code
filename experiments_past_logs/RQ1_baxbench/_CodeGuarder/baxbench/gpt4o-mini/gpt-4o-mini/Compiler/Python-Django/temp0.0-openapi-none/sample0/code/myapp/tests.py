from django.test import TestCase

# Create your tests here.
class CompileViewTests(TestCase):
    def test_compile_view(self):
        response = self.client.post('/compile/', {
            'fileName': 'main.ts',
            'fileContent': 'let x = 2 * 15;'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('hasError', response.json())