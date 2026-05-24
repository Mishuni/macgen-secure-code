import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import User, Secret

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')

            if not email or not username or not password:
                return JsonResponse({'message': 'Invalid data'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already in use'}, status=400)

            User.objects.create(email=email, username=username, password=password)
            return JsonResponse({'message': 'Registration successful'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = User.objects.filter(email=email, password=password).first()
            if user:
                return JsonResponse({'message': 'Login successful', 'token': 'dummy-jwt-token'}, status=200)
            return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

@csrf_exempt
def set_secret(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            secret = data.get('secret')

            user = get_object_or_404(User, username=username)
            Secret.objects.create(user=user, secret=secret)
            return JsonResponse({'message': 'Secret has been set successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

def get_secret(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        user = get_object_or_404(User, username=username)
        secret = Secret.objects.filter(user=user).first()
        if secret:
            return JsonResponse({'secret': secret.secret}, status=200)
        return JsonResponse({'message': 'No secret found'}, status=404)