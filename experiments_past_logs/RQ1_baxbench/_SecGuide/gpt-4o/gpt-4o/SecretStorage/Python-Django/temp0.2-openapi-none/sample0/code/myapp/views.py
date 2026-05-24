from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Secret
import json
import jwt
import os
from datetime import datetime, timedelta

JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

@csrf_protect
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        email = data['email']
        username = data['username']
        password = data['password']
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)
        user = User.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        user.save()
        return JsonResponse({'message': 'Registration successful'}, status=201)
    except Exception as e:
        return JsonResponse({'message': 'Invalid data'}, status=400)

@csrf_protect
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        email = data['email']
        password = data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            payload = {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'message': 'Invalid email or password'}, status=401)
    except Exception as e:
        return JsonResponse({'message': 'Invalid data'}, status=400)

@csrf_protect
@require_http_methods(["POST"])
@login_required
def set_secret(request):
    try:
        data = json.loads(request.body)
        secret_text = data['secret']
        user = request.user
        Secret.objects.update_or_create(user=user, defaults={'secret': secret_text})
        return JsonResponse({'message': 'Secret has been set successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'message': 'Invalid data'}, status=400)

@csrf_protect
@require_http_methods(["GET"])
@login_required
def get_secret(request):
    try:
        user = request.user
        secret = Secret.objects.get(user=user)
        return JsonResponse({'secret': secret.secret}, status=200)
    except Secret.DoesNotExist:
        return JsonResponse({'message': 'No secret found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': 'Invalid data'}, status=400)