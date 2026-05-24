from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageUploadTest(TestCase):
    def test_upload_image(self):
        with open('test_image.jpg', 'rb') as img:
            response = self.client.post(reverse('upload_image'), {'file': img})
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())

    def test_view_image_not_found(self):
        response = self.client.get(reverse('view_image', args=['nonexistent-id']))
        self.assertEqual(response.status_code, 404)