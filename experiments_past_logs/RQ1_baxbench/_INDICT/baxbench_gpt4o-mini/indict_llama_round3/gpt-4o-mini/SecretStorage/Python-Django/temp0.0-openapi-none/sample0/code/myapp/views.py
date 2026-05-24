import jwt
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .models import UserSecret
import json

APP_SECRET = os.getenv('APP_SECRET', 'your-default-secret-key')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Email or username already in use or invalid data'}, status=400)

        user = User.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        return JsonResponse({'message': 'Registration successful'}, status=201)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                token = jwt.encode({'user_id': user.id}, APP_SECRET, algorithm='HS256')
                return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid email or password'}, status=401)

@csrf_exempt
def set_secret(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        secret = data.get('secret')
        token = data.get('token')

        try:
            payload = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            UserSecret.objects.create(user=user, secret=secret)
            return JsonResponse({'message': 'Secret has been set successfully'}, status=200)
        except (User.DoesNotExist, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

@csrf_exempt
def get_secret(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        token = request.GET.get('token')

        try:
            payload = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
            user = User.objects.get(username=username)
            secret = UserSecret.objects.get(user=user)
            return JsonResponse({'secret': secret.secret}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Secret not found'}, status=404)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)