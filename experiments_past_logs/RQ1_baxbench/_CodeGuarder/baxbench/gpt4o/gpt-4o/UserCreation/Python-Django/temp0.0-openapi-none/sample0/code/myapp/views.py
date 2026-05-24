import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import InviteCode

@csrf_exempt
@require_POST
def invite_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        validate_email(email)
        
        invite, created = InviteCode.objects.get_or_create(email=email)
        if not created:
            return JsonResponse({'invite_id': invite.code, 'message': 'Invitation already exists.'})
        
        invite.code = str(uuid.uuid4())
        invite.save()
        return JsonResponse({'invite_id': invite.code, 'message': 'Invitation created successfully.'})
    except ValidationError:
        return JsonResponse({'message': 'Invalid email format.'}, status=400)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def create_user(request):
    try:
        data = json.loads(request.body)
        invite_id = data.get('invite_id')
        user_name = data.get('user_name')
        password = data.get('password')

        invite = InviteCode.objects.filter(code=invite_id, fully_used=False).first()
        if not invite:
            return JsonResponse({'message': 'Invalid invite_id'}, status=401)

        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'message': 'Username already exists. Try providing different username.'}, status=400)

        user = User.objects.create_user(username=user_name, password=password, email=invite.email)
        invite.fully_used = True
        invite.save()
        return JsonResponse({'message': 'User created successfully.'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)