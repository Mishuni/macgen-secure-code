from django.test import TestCase
from django.urls import reverse
from .models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile

class ProfileTests(TestCase):

    def test_add_profile(self):
        response = self.client.post(reverse('add_profile'), {
            'username': 'testuser',
            'profile_page': '<h1>Test User</h1>',
            'profile_photo': SimpleUploadedFile('test.png', b'file_content', content_type='image/png')
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Profile.objects.filter(username='testuser').exists())

    def test_get_profile(self):
        Profile.objects.create(username='testuser', profile_page='<h1>Test User</h1>')
        response = self.client.get(reverse('get_profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Test User</h1>')

    def test_get_profile_photo(self):
        profile = Profile.objects.create(username='testuser', profile_page='<h1>Test User</h1>')
        profile.profile_photo.save('test.png', SimpleUploadedFile('test.png', b'file_content', content_type='image/png'))
        response = self.client.get(reverse('get_profile_photo', args=['testuser']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')