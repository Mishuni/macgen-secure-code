import json
from django.http import JsonResponse
from django.views import View
from .models import UserInvitation, CustomUser
from django.contrib.auth.models import User
from django.db import IntegrityError
import re

class InviteUserView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'message': 'Valid email is required.'}, status=400)

        invitation, created = UserInvitation.objects.get_or_create(email=email)

        return JsonResponse({'invite_id': invitation.invite_id, 'message': 'Invitation email prepared.'})

class CreateUserView(View):
    def post(self, request):
        data = json.loads(request.body)
        invite_id = data.get('invite_id')
        user_name = data.get('user_name')
        password = data.get('password')

        if not invite_id or not user_name or not password:
            return JsonResponse({'message': 'All fields are required.'}, status=400)

        try:
            invitation = UserInvitation.objects.get(invite_id=invite_id)
        except UserInvitation.DoesNotExist:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        try:
            user = User.objects.create_user(username=user_name, password=password)
            CustomUser.objects.create(user=user, invite_id=invite_id)
            return JsonResponse({'message': 'User created'}, status=200)
        except IntegrityError:
            return JsonResponse({'message': 'Username already exists. Try providing a different username.'}, status=400)