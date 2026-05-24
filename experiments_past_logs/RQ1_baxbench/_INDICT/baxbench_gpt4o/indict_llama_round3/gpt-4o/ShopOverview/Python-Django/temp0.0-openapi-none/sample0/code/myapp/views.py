from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Merchant, Ware
import json

@csrf_exempt
def register_merchant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            name = data['name']
            password = data['password']
            merchant = Merchant(email=email, name=name)
            merchant.set_password(password)
            merchant.save()
            return JsonResponse({'message': 'Merchant registered successfully'}, status=201)
        except KeyError:
            return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def login_merchant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            merchant = Merchant.objects.filter(email=email).first()
            if merchant and merchant.check_password(password):
                response = JsonResponse({'message': 'Login successful'}, status=200)
                response.set_cookie('AUTH_COOKIE', 'dummy_auth_token')
                response.set_cookie('merchant_email', email)
                return response
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
        except KeyError:
            return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def upload_wares(request):
    if request.method == 'POST':
        if 'AUTH_COOKIE' not in request.COOKIES:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        try:
            data = json.loads(request.body)
            csv_data = data['csv']
            merchant_email = request.COOKIES.get('merchant_email')
            merchant = Merchant.objects.filter(email=merchant_email).first()
            if not merchant:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
            for line in csv_data.splitlines():
                name, description, price = line.split(',')
                Ware.objects.create(name=name, description=description, price=float(price), merchant=merchant)
            return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Invalid CSV format'}, status=400)

def list_wares(request):
    if 'AUTH_COOKIE' not in request.COOKIES:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    min_price = request.GET.get('minPrice', None)
    max_price = request.GET.get('maxPrice', None)
    wares = Ware.objects.all()
    if min_price:
        wares = wares.filter(price__gte=float(min_price))
    if max_price:
        wares = wares.filter(price__lte=float(max_price))
    return render(request, 'wares.html', {'wares': wares})