import json
import re
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Secret
import jwt
import os

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'message': 'Invalid email'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)

        user = User(email=email, username=username, password=make_password(password))
        user.save()
        return JsonResponse({'message': 'Registration successful'}, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            token = jwt.encode({'user_id': user.id}, os.getenv('APP_SECRET'), algorithm='HS256')
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)

        return JsonResponse({'message': 'Invalid email or password'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class SetSecretView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        secret_text = data.get('secret')
        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        Secret.objects.create(user=user, secret_text=secret_text)
        return JsonResponse({'message': 'Secret has been set successfully'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class GetSecretView(View):
    def get(self, request):
        username = request.GET.get('username')
        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

        secret = Secret.objects.filter(user=user).last()
        return JsonResponse({'secret': secret.secret_text}, status=200) if secret else JsonResponse({'secret': None}, status=200)