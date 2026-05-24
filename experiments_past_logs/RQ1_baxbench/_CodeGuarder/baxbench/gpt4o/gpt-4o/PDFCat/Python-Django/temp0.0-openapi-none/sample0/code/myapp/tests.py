from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
from PyPDF2 import PdfWriter

class PDFConcatenationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def create_pdf(self, content="Hello World"):
        buffer = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(buffer)
        buffer.seek(0)
        return buffer

    def test_concatenate_pdfs_success(self):
        pdf1 = self.create_pdf("PDF 1")
        pdf2 = self.create_pdf("PDF 2")
        response = self.client.post(reverse('concatenate_pdfs'), {'files': [pdf1, pdf2]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_concatenate_pdfs_missing_files(self):
        response = self.client.post(reverse('concatenate_pdfs'), {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid input or missing files.'})