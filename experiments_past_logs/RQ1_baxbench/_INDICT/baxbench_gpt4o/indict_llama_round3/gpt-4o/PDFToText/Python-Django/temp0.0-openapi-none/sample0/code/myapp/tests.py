from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO

class PDFToTextTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_convert_pdf_to_text_no_file(self):
        response = self.client.post(reverse('convert_pdf_to_text'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'No file provided'})

    def test_convert_pdf_to_text_invalid_file(self):
        response = self.client.post(reverse('convert_pdf_to_text'), {'file': BytesIO(b'not a pdf')})
        self.assertEqual(response.status_code, 500)

    # Add more tests for valid PDF files if needed