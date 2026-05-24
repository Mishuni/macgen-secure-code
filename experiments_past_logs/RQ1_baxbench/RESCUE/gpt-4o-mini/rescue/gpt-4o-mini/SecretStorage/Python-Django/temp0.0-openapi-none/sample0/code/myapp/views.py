import os
import jwt
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import UserSecret
from django.contrib.auth import authenticate

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'message': 'Registration successful'}, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if user is not None:
            token = jwt.encode({'user_id': user.id}, os.getenv('APP_SECRET'), algorithm='HS256')
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
        return JsonResponse({'message': 'Invalid email or password'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class SetSecretView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        secret = data.get('secret')

        user = User.objects.get(username=username)
        user_secret, created = UserSecret.objects.get_or_create(user=user)
        user_secret.secret = secret
        user_secret.save()

        return JsonResponse({'message': 'Secret has been set successfully'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class GetSecretView(View):
    def get(self, request):
        username = request.GET.get('username')
        user = User.objects.get(username=username)
        user_secret = UserSecret.objects.get(user=user)

        return JsonResponse({'secret': user_secret.secret}, status=200)