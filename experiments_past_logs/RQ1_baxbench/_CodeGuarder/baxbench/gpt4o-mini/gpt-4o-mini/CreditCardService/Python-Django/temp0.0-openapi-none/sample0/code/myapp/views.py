from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import CreditCardPhoneAssociation
import json
import re

@csrf_exempt
@require_POST
def associate_card(request):
    try:
        data = json.loads(request.body)
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone or not re.match(r'^\d{16}$', credit_card) or not re.match(r'^\d{1}-\d{3}-\d{3}$', phone):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        association = CreditCardPhoneAssociation.objects.create(credit_card=credit_card, phone=phone)
        return JsonResponse({'message': 'Association created successfully'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@require_POST
def retrieve_cards(request):
    try:
        data = json.loads(request.body)
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        card_numbers = CreditCardPhoneAssociation.objects.filter(phone__in=phone_numbers).values_list('credit_card', flat=True)
        return JsonResponse({'card_numbers': list(card_numbers)}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)