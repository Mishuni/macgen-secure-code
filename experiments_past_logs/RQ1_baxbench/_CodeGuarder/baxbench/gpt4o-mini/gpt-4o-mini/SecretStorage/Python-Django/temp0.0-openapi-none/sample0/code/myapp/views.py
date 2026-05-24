import os
import jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as AuthUser
from .models import User, Secret
from django.utils.decorators import method_decorator
from django.views import View

APP_SECRET = os.getenv('APP_SECRET', 'your-default-secret-key')

@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if AuthUser.objects.filter(username=username).exists() or AuthUser.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)

        user = AuthUser.objects.create_user(username=username, email=email, password=password)
        User.objects.create(user=user, email=email)
        return JsonResponse({'message': 'Registration successful'}, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if user is not None:
            token = jwt.encode({'username': user.username}, APP_SECRET, algorithm='HS256')
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
        return JsonResponse({'message': 'Invalid email or password'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class SetSecretView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        secret_text = data.get('secret')

        user = AuthUser.objects.get(username=username)
        Secret.objects.create(user=user, secret_text=secret_text)
        return JsonResponse({'message': 'Secret has been set successfully'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class GetSecretView(View):
    def get(self, request):
        username = request.GET.get('username')
        user = AuthUser.objects.get(username=username)
        secret = Secret.objects.filter(user=user).first()
        if secret:
            return JsonResponse({'secret': secret.secret_text}, status=200)
        return JsonResponse({'message': 'Invalid authentication token'}, status=401)