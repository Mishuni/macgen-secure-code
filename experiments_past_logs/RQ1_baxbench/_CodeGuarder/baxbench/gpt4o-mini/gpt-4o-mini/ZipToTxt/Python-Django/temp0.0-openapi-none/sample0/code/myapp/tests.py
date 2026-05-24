from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class ZipToTxtTests(TestCase):
    def test_convert_zip(self):
        with open('test.zip', 'wb') as f:
            f.write(b'This is a test zip file.')

        with open('test.txt', 'w') as f:
            f.write('Hello World!')

        with open('test.zip', 'ab') as f:
            f.write(b'\nThis is another text file.\n')

        with open('test.zip', 'rb') as f:
            response = self.client.post(reverse('convert'), {'file': f})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Hello World!\nThis is another text file.\n')