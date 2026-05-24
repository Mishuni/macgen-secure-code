from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import InviteCode

class InviteUserTestCase(TestCase):
    def test_invite_user(self):
        response = self.client.post(reverse('invite_user'), {'email': 'test@example.com'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('invite_id', response.json())

    def test_create_user(self):
        invite = InviteCode.objects.create(email='test@example.com', code='testcode')
        response = self.client.post(reverse('create_user'), {'invite_id': 'testcode', 'user_name': 'testuser', 'password': 'testpass'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='testuser').exists())