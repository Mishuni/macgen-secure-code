import secrets
import logging
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .models import Invitation
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@csrf_protect
@require_http_methods(["POST"])
def invite_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'message': 'Email is required'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'message': 'Invalid email format'}, status=400)

        invitation, created = Invitation.objects.get_or_create(email=email)
        if created:
            invitation.invite_id = secrets.token_urlsafe(16)
            invitation.save()

        return JsonResponse({'invite_id': invitation.invite_id, 'message': 'Invitation created'}, status=200)
    except Exception as e:
        logger.error(f"Error in invite_user: {str(e)}")
        return JsonResponse({'message': 'An error occurred'}, status=500)

@csrf_protect
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
        except Invitation.DoesNotExist:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)

        # Use Django's built-in password hashing
        user = User.objects.create_user(username=user_name, password=password)
        user.save()

        # Optionally, delete the invitation after use
        invitation.delete()

        return JsonResponse({'message': 'User created'}, status=200)
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        return JsonResponse({'message': 'An error occurred'}, status=500)