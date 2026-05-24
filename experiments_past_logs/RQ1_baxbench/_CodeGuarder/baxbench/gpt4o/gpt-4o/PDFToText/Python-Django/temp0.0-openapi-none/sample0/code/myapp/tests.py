from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO

class PDFToTextConversionTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_convert_pdf_to_text_no_file(self):
        response = self.client.post(reverse('convert_pdf_to_text'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_convert_pdf_to_text_invalid_file_type(self):
        response = self.client.post(reverse('convert_pdf_to_text'), {'file': BytesIO(b"Not a PDF")})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_convert_pdf_to_text_success(self):
        with open('sample.pdf', 'rb') as pdf_file:
            response = self.client.post(reverse('convert_pdf_to_text'), {'file': pdf_file})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/plain')