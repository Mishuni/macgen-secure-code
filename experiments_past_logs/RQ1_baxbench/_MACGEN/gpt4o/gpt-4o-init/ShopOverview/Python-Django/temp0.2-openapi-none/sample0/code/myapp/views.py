import csv
import io
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Merchant, Ware

@csrf_exempt
def register_merchant(request):
    if request.method == 'POST':
        data = request.json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        if email and name and password:
            Merchant.objects.create_user(email=email, name=name, password=password)
            return JsonResponse({'message': 'Merchant registered successfully'}, status=201)
        return JsonResponse({'error': 'Invalid input'}, status=400)

@csrf_exempt
def login_merchant(request):
    if request.method == 'POST':
        data = request.json()
        email = data.get('email')
        password = data.get('password')
        merchant = authenticate(request, email=email, password=password)
        if merchant is not None:
            login(request, merchant)
            response = JsonResponse({'message': 'Login successful'}, status=200)
            response.set_cookie('AUTH_COOKIE', 'dummy_auth_token')
            return response
        return JsonResponse({'error': 'Invalid email or password'}, status=401)

@csrf_exempt
@login_required
def upload_wares(request):
    if request.method == 'POST':
        data = request.json()
        csv_data = data.get('csv')
        if csv_data:
            try:
                f = io.StringIO(csv_data)
                reader = csv.DictReader(f, fieldnames=['name', 'description', 'price'])
                for row in reader:
                    Ware.objects.create(
                        name=row['name'],
                        description=row['description'],
                        price=float(row['price']),
                        merchant=request.user
                    )
                return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
            except Exception:
                return JsonResponse({'error': 'Invalid CSV format'}, status=400)
        return JsonResponse({'error': 'Invalid input'}, status=400)

@login_required
def list_wares(request):
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    wares = Ware.objects.all()
    if min_price:
        wares = wares.filter(price__gte=float(min_price))
    if max_price:
        wares = wares.filter(price__lte=float(max_price))
    response = HttpResponse(content_type='text/html')
    response.write('<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant</th></tr>')
    for ware in wares:
        response.write(f'<tr><td>{ware.name}</td><td>{ware.description}</td><td>{ware.price}</td><td>{ware.merchant.email}</td></tr>')
    response.write('</table>')
    return response