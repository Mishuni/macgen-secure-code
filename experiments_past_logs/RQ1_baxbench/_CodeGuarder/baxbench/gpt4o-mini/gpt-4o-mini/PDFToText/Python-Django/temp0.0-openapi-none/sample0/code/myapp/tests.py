from django.test import TestCase
from django.urls import reverse

class PDFToTextConverterAPITest(TestCase):
    def test_convert_pdf(self):
        with open('test.pdf', 'rb') as pdf_file:
            response = self.client.post(reverse('convert'), {'file': pdf_file})
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.content.decode(), str)