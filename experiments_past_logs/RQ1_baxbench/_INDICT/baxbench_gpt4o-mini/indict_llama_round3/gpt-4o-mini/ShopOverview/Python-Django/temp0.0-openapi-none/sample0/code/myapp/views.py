from django.shortcuts import render
from django.http import JsonResponse
from .models import Merchant, Ware
import csv
import io
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_merchant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        if email and name and password:
            merchant = Merchant(email=email, name=name, password=password)
            merchant.save()
            return JsonResponse({'message': 'Merchant registered successfully'}, status=201)
        return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def login_merchant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        try:
            merchant = Merchant.objects.get(email=email, password=password)
            response = JsonResponse('Login successful', safe=False, status=200)
            response.set_cookie('AUTH_COOKIE', 'some_cookie_value')  # Simulate setting a cookie
            return response
        except Merchant.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

@csrf_exempt
def upload_wares(request):
    if request.method == 'POST':
        if 'AUTH_COOKIE' not in request.COOKIES:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        data = json.loads(request.body)
        csv_data = data.get('csv')
        if csv_data:
            try:
                decoded_file = io.StringIO(csv_data)
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    merchant = Merchant.objects.get(email=row['merchant_email'])  # Assuming merchant_email is provided in CSV
                    ware = Ware(
                        name=row['name'],
                        description=row['description'],
                        price=float(row['price']),
                        merchant=merchant
                    )
                    ware.save()
                return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
            except Exception as e:
                return JsonResponse({'error': 'Invalid CSV format'}, status=400)
        return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def get_wares(request):
    if 'AUTH_COOKIE' not in request.COOKIES:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    wares = Ware.objects.all()
    
    if min_price:
        wares = wares.filter(price__gte=float(min_price))
    if max_price:
        wares = wares.filter(price__lte=float(max_price))

    return render(request, 'wares.html', {'wares': wares})