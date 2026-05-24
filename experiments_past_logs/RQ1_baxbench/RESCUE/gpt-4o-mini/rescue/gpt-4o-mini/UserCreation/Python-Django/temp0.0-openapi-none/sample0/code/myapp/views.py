import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Invitation, User
import uuid

@csrf_exempt
def invite_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'message': 'Email is required.'}, status=400)

            invite_id = str(uuid.uuid4())
            invitation, created = Invitation.objects.get_or_create(email=email, defaults={'invite_id': invite_id})

            if not created:
                invite_id = invitation.invite_id

            return JsonResponse({'invite_id': invite_id, 'message': 'Invitation email sent.'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invite_id = data.get('invite_id')
            username = data.get('user_name')
            password = data.get('password')

            if not invite_id or not username or not password:
                return JsonResponse({'message': 'All fields are required.'}, status=400)

            try:
                invitation = Invitation.objects.get(invite_id=invite_id)
            except Invitation.DoesNotExist:
                return JsonResponse({'message': 'Invalid invite_id.'}, status=401)

            user = User(username=username, password=password, invitation=invitation)
            user.save()

            return JsonResponse({'message': 'User created.'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)