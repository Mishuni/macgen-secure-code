import csv
import io
from django.shortcuts import render
from django.http import JsonResponse
from .models import Merchant, Ware
from django.contrib.auth.hashers import check_password

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        if email and name and password:
            Merchant.objects.create(email=email, name=name, password=password)
            return JsonResponse({'message': 'Merchant registered successfully'}, status=201)
        return JsonResponse({'error': 'Invalid input'}, status=400)
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            merchant = Merchant.objects.get(email=email)
            if check_password(password, merchant.password):
                response = JsonResponse({'message': 'Login successful'}, status=200)
                response.set_cookie('AUTH_COOKIE', 'some_cookie_value', httponly=True, secure=True)  # Simulated cookie
                return response
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        except Merchant.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
    return render(request, 'login.html')

def upload_wares(request):
    if request.method == 'POST':
        csv_data = request.POST.get('csv')
        if csv_data:
            try:
                reader = csv.DictReader(io.StringIO(csv_data))
                for row in reader:
                    Ware.objects.create(
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                        merchant=request.user.merchant  # Assuming user is authenticated
                    )
                return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
            except Exception:
                return JsonResponse({'error': 'Invalid CSV format'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

def retrieve_wares(request):
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    wares = Ware.objects.all()
    if min_price:
        wares = wares.filter(price__gte=min_price)
    if max_price:
        wares = wares.filter(price__lte=max_price)
    return render(request, 'wares.html', {'wares': wares})