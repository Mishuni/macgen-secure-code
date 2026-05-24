import uuid
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Invitation
import json

@csrf_exempt
def invite_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'message': 'Invalid email format.'}, status=400)

        invitation, created = Invitation.objects.get_or_create(email=email)
        if not created:
            invite_id = invitation.invite_id
        else:
            invite_id = str(uuid.uuid4())
            invitation.invite_id = invite_id
            invitation.save()

        return JsonResponse({'invite_id': invite_id, 'message': 'Invitation email sent.'})

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        invite_id = data.get('invite_id')
        user_name = data.get('user_name')
        password = data.get('password')

        try:
            invitation = Invitation.objects.get(invite_id=invite_id)
        except Invitation.DoesNotExist:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)

        user = User(username=user_name, email=invitation.email)
        user.set_password(password)
        user.save()
        return JsonResponse({'message': 'User created'})