import csv
import io
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Merchant, Ware

@csrf_exempt
def register_merchant(request):
    if request.method == 'POST':
        data = request.POST
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        if not email or not name or not password:
            return JsonResponse({'error': 'Invalid input'}, status=400)
        try:
            merchant = Merchant.objects.create_user(email=email, name=name, password=password)
            return JsonResponse({'message': 'Merchant registered successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def login_merchant(request):
    if request.method == 'POST':
        data = request.POST
        email = data.get('email')
        password = data.get('password')
        merchant = authenticate(request, email=email, password=password)
        if merchant is not None:
            login(request, merchant)
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

@csrf_exempt
@login_required
def upload_wares(request):
    if request.method == 'POST':
        data = request.POST
        csv_data = data.get('csv')
        if not csv_data:
            return JsonResponse({'error': 'Invalid CSV format'}, status=400)
        try:
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file, fieldnames=['name', 'description', 'price'])
            for row in reader:
                Ware.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=float(row['price']),
                    merchant=request.user
                )
            return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def list_wares(request):
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    wares = Ware.objects.all()
    if min_price:
        wares = wares.filter(price__gte=float(min_price))
    if max_price:
        wares = wares.filter(price__lte=float(max_price))
    return render(request, 'wares_list.html', {'wares': wares})