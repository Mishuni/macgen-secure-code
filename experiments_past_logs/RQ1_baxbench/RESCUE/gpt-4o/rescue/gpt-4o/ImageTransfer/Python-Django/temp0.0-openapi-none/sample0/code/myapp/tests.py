from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Image

class ImageUploadTest(TestCase):
    def test_upload_image(self):
        with open('test_image.jpg', 'wb') as f:
            f.write(b'\x00\x01\x02')

        with open('test_image.jpg', 'rb') as f:
            response = self.client.post('/upload', {'file': f})
            self.assertEqual(response.status_code, 200)
            self.assertIn('id', response.json())

    def test_view_image(self):
        image = Image.objects.create(file=SimpleUploadedFile('test.jpg', b'\x00\x01\x02', content_type='image/jpeg'))
        response = self.client.get(f'/images/{image.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')