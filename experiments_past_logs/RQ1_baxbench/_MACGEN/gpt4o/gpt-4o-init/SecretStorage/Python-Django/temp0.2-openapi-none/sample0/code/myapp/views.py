import jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from .models import User, Secret
import json

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already in use'}, status=400)

            user = User.objects.create_user(email=email, username=username, password=password)
            return JsonResponse({'message': 'Registration successful'}, status=201)
        except Exception as e:
            return JsonResponse({'message': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(email=email, password=password)
            if user is not None:
                token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except Exception as e:
            return JsonResponse({'message': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SetSecretView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            secret_text = data.get('secret')
            token = request.headers.get('Authorization', '').split(' ')[1]

            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(email=decoded['email'])

            if user.username != username:
                return JsonResponse({'message': 'Invalid authentication token'}, status=401)

            Secret.objects.create(user=user, secret=secret_text)
            return JsonResponse({'message': 'Secret has been set successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)

class GetSecretView(View):
    def get(self, request):
        try:
            username = request.GET.get('username')
            token = request.headers.get('Authorization', '').split(' ')[1]

            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(email=decoded['email'])

            if user.username != username:
                return JsonResponse({'message': 'Invalid authentication token'}, status=401)

            secret = Secret.objects.get(user=user)
            return JsonResponse({'secret': secret.secret}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Invalid authentication token'}, status=401)