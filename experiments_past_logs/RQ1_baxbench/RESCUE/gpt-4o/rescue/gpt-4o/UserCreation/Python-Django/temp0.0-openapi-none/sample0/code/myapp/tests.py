from django.test import TestCase
from .models import Invitation, User

class InvitationModelTest(TestCase):
    def test_create_invitation(self):
        invitation = Invitation.objects.create(email="test@example.com", invite_id="12345")
        self.assertEqual(invitation.email, "test@example.com")

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(user_name="testuser", password="password123")
        self.assertEqual(user.user_name, "testuser")