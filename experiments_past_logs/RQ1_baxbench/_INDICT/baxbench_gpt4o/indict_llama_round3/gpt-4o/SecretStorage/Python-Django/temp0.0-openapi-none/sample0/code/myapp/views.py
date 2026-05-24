import jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from .models import Secret
import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return JsonResponse({'message': 'Registration successful'}, status=201)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                token = jwt.encode({'username': user.username}, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid email or password'}, status=401)

@csrf_exempt
def set_secret(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username = payload.get('username')
            user = User.objects.get(username=username)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        data = json.loads(request.body)
        secret_text = data.get('secret')

        secret, created = Secret.objects.get_or_create(user=user)
        secret.secret = secret_text
        secret.save()
        return JsonResponse({'message': 'Secret has been set successfully'}, status=200)

@csrf_exempt
def get_secret(request):
    if request.method == 'GET':
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username = payload.get('username')
            user = User.objects.get(username=username)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        try:
            secret = Secret.objects.get(user=user)
            return JsonResponse({'secret': secret.secret}, status=200)
        except Secret.DoesNotExist:
            return JsonResponse({'message': 'No secret found for this user'}, status=404)