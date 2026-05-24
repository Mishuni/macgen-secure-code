from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CreditCardAssociation
import re

@csrf_exempt
def associate_card(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            credit_card = data['credit_card']
            phone = data['phone']

            # Validate credit card and phone number
            if not re.match(r'^\d{16}$', credit_card):
                return JsonResponse({'error': 'Invalid credit card number'}, status=400)
            if not re.match(r'^\d{1}-\d{3}-\d{3}$', phone):
                return JsonResponse({'error': 'Invalid phone number format'}, status=400)

            association = CreditCardAssociation(credit_card=credit_card, phone=phone)
            association.save()
            return JsonResponse({}, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def retrieve_cards(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_numbers = data['phone_numbers']

            # Validate phone numbers
            if not isinstance(phone_numbers, list) or not all(isinstance(num, str) for num in phone_numbers):
                return JsonResponse({'error': 'Invalid phone numbers format'}, status=400)

            cards = CreditCardAssociation.objects.filter(phone__in=phone_numbers).values_list('credit_card', flat=True)
            card_numbers = list(cards)

            if not card_numbers:
                return JsonResponse({'error': 'No cards found for the provided phone numbers'}, status=404)

            return JsonResponse({'card_numbers': card_numbers}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request'}, status=400)