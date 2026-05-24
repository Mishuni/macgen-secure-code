import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User
import jwt
import os

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            user = User.objects.filter(email=email).first()
            if user and check_password(password, user.password):
                token = jwt.encode({'email': user.email}, os.environ.get('APP_SECRET', 'default-secret-key'), algorithm='HS256')
                return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except Exception as e:
            return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already in use'}, status=400)
            user = User(email=email, password=make_password(password), name=name)
            user.save()
            return JsonResponse({'message': 'Registration successful'}, status=201)
        except Exception as e:
            return JsonResponse({'message': 'Invalid request'}, status=400)