import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Invitation
import json

@csrf_exempt
def invite_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            validate_email(email)
        except (ValidationError, KeyError, json.JSONDecodeError):
            return JsonResponse({'message': 'Invalid email format'}, status=400)

        invitation, created = Invitation.objects.get_or_create(email=email)
        if created:
            invitation.invite_id = str(uuid.uuid4())
            invitation.save()

        return JsonResponse({'invite_id': invitation.invite_id, 'message': 'Invitation created'})

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invite_id = data.get('invite_id')
            user_name = data.get('user_name')
            password = data.get('password')
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'message': 'Invalid input'}, status=400)

        try:
            invitation = Invitation.objects.get(invite_id=invite_id)
        except Invitation.DoesNotExist:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)

        User.objects.create_user(username=user_name, password=password)
        invitation.delete()

        return JsonResponse({'message': 'User created'})