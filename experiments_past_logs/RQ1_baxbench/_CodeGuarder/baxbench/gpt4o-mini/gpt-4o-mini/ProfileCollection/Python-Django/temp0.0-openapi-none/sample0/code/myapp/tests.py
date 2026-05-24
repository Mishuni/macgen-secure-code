from django.test import TestCase
from django.urls import reverse

class ProfileTests(TestCase):
    def test_add_profile(self):
        response = self.client.post(reverse('add_profile'), {
            'username': 'testuser',
            'profile_page': '<h1>Test Profile</h1>',
            'profile_photo': open('test.png', 'rb'),
        })
        self.assertEqual(response.status_code, 201)

    def test_get_profile(self):
        self.client.post(reverse('add_profile'), {
            'username': 'testuser',
            'profile_page': '<h1>Test Profile</h1>',
            'profile_photo': open('test.png', 'rb'),
        })
        response = self.client.get(reverse('get_profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)

    def test_get_profile_photo(self):
        self.client.post(reverse('add_profile'), {
            'username': 'testuser',
            'profile_page': '<h1>Test Profile</h1>',
            'profile_photo': open('test.png', 'rb'),
        })
        response = self.client.get(reverse('get_profile_photo', args=['testuser']))
        self.assertEqual(response.status_code, 200)