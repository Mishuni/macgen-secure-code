from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
import zipfile

class ConvertZipToTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_convert_zip_to_txt_success(self):
        # Create a zip file in memory
        in_memory_zip = BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w') as zf:
            zf.writestr('file1.txt', 'Hello World')
            zf.writestr('file2.txt', 'Django Test')

        in_memory_zip.seek(0)

        response = self.client.post(reverse('convert_zip_to_txt'), {'file': in_memory_zip}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello World', response.content.decode())
        self.assertIn('Django Test', response.content.decode())

    def test_convert_zip_to_txt_no_file(self):
        response = self.client.post(reverse('convert_zip_to_txt'), {}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_convert_zip_to_txt_invalid_zip(self):
        invalid_file = BytesIO(b'Not a zip file')
        response = self.client.post(reverse('convert_zip_to_txt'), {'file': invalid_file}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_convert_zip_to_txt_large_file(self):
        large_file = BytesIO(b'\0' * (10 * 1024 * 1024 + 1))  # Just over 10 MB
        response = self.client.post(reverse('convert_zip_to_txt'), {'file': large_file}, format='multipart')
        self.assertEqual(response.status_code, 400)