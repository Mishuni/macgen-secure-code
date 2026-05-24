import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import json
from .models import Invitation, User

@csrf_exempt
@require_http_methods(["POST"])
def invite_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'message': 'Email is required'}, status=400)

        invitation, created = Invitation.objects.get_or_create(email=email, defaults={'invite_id': str(uuid.uuid4())})
        return JsonResponse({'invite_id': invitation.invite_id, 'message': 'Invitation created' if created else 'Invitation already exists'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    try:
        data = json.loads(request.body)
        invite_id = data.get('invite_id')
        user_name = data.get('user_name')
        password = data.get('password')

        if not invite_id or not user_name or not password:
            return JsonResponse({'message': 'All fields are required'}, status=400)

        try:
            invitation = Invitation.objects.get(invite_id=invite_id)
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        try:
            User.objects.create(user_name=user_name, password=password)
            return JsonResponse({'message': 'User created'}, status=200)
        except IntegrityError:
            return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)