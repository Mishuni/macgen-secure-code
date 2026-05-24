from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Merchant, Ware
import json

@csrf_exempt
def register_merchant(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data["email"]
            name = data["name"]
            password = data["password"]
            Merchant.objects.create(email=email, name=name, password=password)
            return JsonResponse({"message": "Merchant registered successfully"}, status=201)
        except KeyError:
            return JsonResponse({"error": "Invalid input"}, status=400)

@csrf_exempt
def login_merchant(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"]
            merchant = Merchant.objects.filter(email=email, password=password).first()
            if merchant:
                response = JsonResponse({"message": "Login successful"})
                response.set_cookie("AUTH_COOKIE", merchant.id)
                return response
            else:
                return JsonResponse({"error": "Invalid email or password"}, status=401)
        except KeyError:
            return JsonResponse({"error": "Invalid input"}, status=400)

@csrf_exempt
def upload_wares(request):
    if request.method == "POST":
        merchant_id = request.COOKIES.get("AUTH_COOKIE")
        if not merchant_id:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        try:
            merchant = Merchant.objects.get(id=merchant_id)
            data = json.loads(request.body)
            csv_data = data["csv"]
            for line in csv_data.splitlines():
                name, description, price = line.split(",")
                Ware.objects.create(name=name, description=description, price=float(price), merchant=merchant)
            return JsonResponse({"message": "Wares uploaded successfully"})
        except Exception:
            return JsonResponse({"error": "Invalid CSV format"}, status=400)

def list_wares(request):
    min_price = request.GET.get("minPrice")
    max_price = request.GET.get("maxPrice")
    wares = Ware.objects.all()
    if min_price:
        wares = wares.filter(price__gte=float(min_price))
    if max_price:
        wares = wares.filter(price__lte=float(max_price))
    return render(request, "wares.html", {"wares": wares})