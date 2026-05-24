import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import jwt
import os

class LoginView(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token = jwt.encode({'user_id': user.id}, os.environ.get('APP_SECRET'), algorithm='HS256')
            return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
        return JsonResponse({'message': 'Invalid email or password'}, status=401)

class RegisterView(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already in use or invalid data'}, status=400)
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        return JsonResponse({'message': 'Registration successful'}, status=201)