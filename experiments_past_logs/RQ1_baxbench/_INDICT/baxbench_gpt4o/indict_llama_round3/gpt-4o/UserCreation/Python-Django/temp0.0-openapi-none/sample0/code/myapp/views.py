import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Invitation
import json
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def invite_user(request):
    data = json.loads(request.body)
    email = data.get('email')
    if not email:
        return JsonResponse({'message': 'Email is required'}, status=400)

    invitation, created = Invitation.objects.get_or_create(email=email)
    if created:
        invitation.invite_id = str(uuid.uuid4())
        invitation.save()

    return JsonResponse({'invite_id': invitation.invite_id, 'message': 'Invitation created'})

@csrf_exempt
@require_POST
def create_user(request):
    data = json.loads(request.body)
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return JsonResponse({'message': 'All fields are required'}, status=400)

    try:
        invitation = Invitation.objects.get(invite_id=invite_id)
    except Invitation.DoesNotExist:
        return JsonResponse({'message': 'Invalid invite_id'}, status=401)

    if User.objects.filter(username=user_name).exists():
        return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)

    User.objects.create(username=user_name, password=make_password(password))
    invitation.delete()

    return JsonResponse({'message': 'User created'})