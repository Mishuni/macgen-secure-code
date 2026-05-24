from django.test import TestCase
from django.urls import reverse
from .models import Invitation
from django.contrib.auth.models import User

class InviteUserTestCase(TestCase):
    def test_invite_user(self):
        response = self.client.post(reverse('invite_user'), {'email': 'test@example.com'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('invite_id', response.json())

class CreateUserTestCase(TestCase):
    def setUp(self):
        self.invitation = Invitation.objects.create(email='test@example.com', invite_id='testinviteid')

    def test_create_user(self):
        response = self.client.post(reverse('create_user'), {
            'invite_id': 'testinviteid',
            'user_name': 'newuser',
            'password': 'newpassword'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)