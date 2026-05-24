from django.test import TestCase
from django.urls import reverse
from .models import Invitation, User

class UserCreationTests(TestCase):
    def setUp(self):
        self.invitation = Invitation.objects.create(email='user@example.com', invite_id='test-invite-id')

    def test_invite_user(self):
        response = self.client.post(reverse('invite_user'), {'email': 'user@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('invite_id', response.json())

    def test_create_user(self):
        response = self.client.post(reverse('create_user'), {
            'invite_id': self.invitation.invite_id,
            'user_name': 'newuser',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'User created')