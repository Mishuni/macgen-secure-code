import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                token = jwt.encode({
                    'user_id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'token': token, 'message': 'Login successful'}, status=200)
            return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except User.DoesNotExist:
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
        user = User.objects.create_user(email=email, password=password, name=name)
        return JsonResponse({'message': 'Registration successful'}, status=201)