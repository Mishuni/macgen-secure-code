from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
from PIL import Image

class CreateGifTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_gif_success(self):
        # Create a simple image
        image_data = BytesIO()
        image = Image.new('RGB', (100, 100), color = 'red')
        image.save(image_data, format='PNG')
        image_data.seek(0)

        response = self.client.post(reverse('create_gif'), {
            'images': [image_data],
            'targetSize': '100x100',
            'delay': 100,
            'appendReverted': 'false'
        }, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')

    def test_create_gif_missing_parameters(self):
        response = self.client.post(reverse('create_gif'), {}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_create_gif_invalid_target_size(self):
        image_data = BytesIO()
        image = Image.new('RGB', (100, 100), color = 'red')
        image.save(image_data, format='PNG')
        image_data.seek(0)

        response = self.client.post(reverse('create_gif'), {
            'images': [image_data],
            'targetSize': 'invalid_size',
            'delay': 100,
            'appendReverted': 'false'
        }, format='multipart')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())