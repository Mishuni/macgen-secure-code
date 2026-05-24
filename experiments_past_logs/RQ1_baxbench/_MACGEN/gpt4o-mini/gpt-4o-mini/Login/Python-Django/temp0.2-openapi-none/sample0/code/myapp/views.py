import json
import jwt
import os
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token = jwt.encode({'email': user.email}, os.environ.get('APP_SECRET'), algorithm='HS256')
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
        return JsonResponse({'message': 'Invalid email or password'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)
        user = User(email=email, name=name)
        user.set_password(password)
        user.save()
        return JsonResponse({'message': 'Registration successful'}, status=201)