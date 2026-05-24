from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CardAssociation
from cryptography.fernet import Fernet
import json
import os

# Generate a key for encryption
key = os.environ.get('APP_SECRET').encode()
cipher = Fernet(key)

@csrf_exempt
def associate_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        # Encrypt the credit card number
        encrypted_card = cipher.encrypt(credit_card.encode()).decode()

        try:
            association = CardAssociation.objects.create(credit_card=encrypted_card, phone=phone)
            return JsonResponse({'message': 'Association created successfully'}, status=201)
        except Exception:
            return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def retrieve_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        associations = CardAssociation.objects.filter(phone__in=phone_numbers)
        if associations.exists():
            card_numbers = [cipher.decrypt(assoc.credit_card.encode()).decode()[-4:] for assoc in associations]
            return JsonResponse({'card_numbers': card_numbers}, status=200)
        else:
            return JsonResponse({'error': 'Not found'}, status=404)