import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            if not email or not password:
                return JsonResponse({'message': 'Email and password are required'}, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'message': 'Invalid email format'}, status=400)

            user = User.objects.filter(email=email, password=password).first()
            if user:
                return JsonResponse({'token': 'jwt-token-abc123', 'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            name = data.get('name', '').strip()

            if not email or not password or not name:
                return JsonResponse({'message': 'Email, password, and name are required'}, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'message': 'Invalid email format'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already in use'}, status=400)

            User.objects.create(email=email, password=password, name=name)
            return JsonResponse({'message': 'Registration successful'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)