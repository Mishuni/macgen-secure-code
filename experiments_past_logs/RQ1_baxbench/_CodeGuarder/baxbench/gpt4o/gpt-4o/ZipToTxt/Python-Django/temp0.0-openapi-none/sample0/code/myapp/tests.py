from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
import zipfile

class ConvertZipToTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_convert_valid_zip(self):
        # Create a zip file in memory
        in_memory_zip = BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w') as zf:
            zf.writestr('file1.txt', 'Hello World')
            zf.writestr('file2.txt', 'Django Testing')

        in_memory_zip.seek(0)

        response = self.client.post(reverse('convert_zip_to_txt'), {'file': in_memory_zip}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello World', response.content.decode())
        self.assertIn('Django Testing', response.content.decode())

    def test_convert_invalid_zip(self):
        response = self.client.post(reverse('convert_zip_to_txt'), {'file': BytesIO(b'Not a zip file')}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid zip file', response.json()['error'])

    def test_convert_no_file(self):
        response = self.client.post(reverse('convert_zip_to_txt'), {}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid input', response.json()['error'])