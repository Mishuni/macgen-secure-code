from django.test import TestCase, Client
from django.urls import reverse
import io
import zipfile

class ConvertZipToTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_convert_zip_to_txt_success(self):
        # Create a zip file in memory
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w') as zf:
            zf.writestr('file1.txt', 'Hello World')
            zf.writestr('file2.txt', 'Goodbye World')
        in_memory_zip.seek(0)

        response = self.client.post(reverse('convert_zip_to_txt'), {'file': in_memory_zip}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello World', response.content.decode())
        self.assertIn('Goodbye World', response.content.decode())

    def test_convert_zip_to_txt_no_file(self):
        response = self.client.post(reverse('convert_zip_to_txt'), {}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_convert_zip_to_txt_invalid_zip(self):
        invalid_file = io.BytesIO(b'Not a zip file')
        response = self.client.post(reverse('convert_zip_to_txt'), {'file': invalid_file}, format='multipart')
        self.assertEqual(response.status_code, 400)