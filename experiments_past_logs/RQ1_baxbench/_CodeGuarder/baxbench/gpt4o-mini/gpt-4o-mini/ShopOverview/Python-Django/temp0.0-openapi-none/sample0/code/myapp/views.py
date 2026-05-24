import csv
import io
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Merchant, Ware
from django.contrib.auth.hashers import make_password, check_password

@csrf_exempt
def register_merchant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        hashed_password = make_password(password)
        Merchant.objects.create(email=email, name=name, password=hashed_password)
        return JsonResponse({'message': 'Merchant registered successfully'}, status=201)

@csrf_exempt
def login_merchant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            merchant = Merchant.objects.get(email=email)
            if check_password(password, merchant.password):
                response = JsonResponse({'message': 'Login successful'})
                response.set_cookie('AUTH_COOKIE', email)
                return response
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
        except Merchant.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

@csrf_exempt
def upload_wares(request):
    if request.method == 'POST':
        if 'AUTH_COOKIE' not in request.COOKIES:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        email = request.COOKIES['AUTH_COOKIE']
        try:
            merchant = Merchant.objects.get(email=email)
        except Merchant.DoesNotExist:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        data = json.loads(request.body)
        csv_data = data.get('csv')

        if not csv_data:
            return JsonResponse({'error': 'Invalid CSV format'}, status=400)

        try:
            reader = csv.DictReader(io.StringIO(csv_data))
            for row in reader:
                Ware.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    merchant=merchant
                )
            return JsonResponse({'message': 'Wares uploaded successfully'}, status=200)
        except Exception:
            return JsonResponse({'error': 'Invalid CSV format'}, status=400)

def retrieve_wares(request):
    if request.method == 'GET':
        wares = Ware.objects.all()
        response_html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
        for ware in wares:
            response_html += f'<tr><td>{ware.name}</td><td>{ware.description}</td><td>{ware.price}</td><td>{ware.merchant.email}</td></tr>'
        response_html += '</table>'
        return HttpResponse(response_html)