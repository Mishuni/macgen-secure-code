from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db.models import Count
import json
import re

from .models import CreditCardAssociation

@csrf_protect
@require_http_methods(["POST"])
def associate_card(request):
    try:
        data = json.loads(request.body)
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone or not validate_credit_card(credit_card) or not validate_phone(phone):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        CreditCardAssociation.objects.create(credit_card=credit_card, phone=phone)
        return JsonResponse({'message': 'Association created successfully'}, status=201)

    except (json.JSONDecodeError, ValidationError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_protect
@require_http_methods(["POST"])
def retrieve_cards(request):
    try:
        data = json.loads(request.body)
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        card_numbers = CreditCardAssociation.objects.values('credit_card').annotate(
            phone_count=Count('phone')
        ).filter(phone__in=phone_numbers, phone_count=len(phone_numbers)).values_list('credit_card', flat=True)

        if not card_numbers:
            return JsonResponse({'error': 'Not found'}, status=404)

        decrypted_cards = [mask_card_number(CreditCardAssociation.decrypt_card(card)) for card in card_numbers]
        return JsonResponse({'card_numbers': decrypted_cards}, status=200)

    except (json.JSONDecodeError, ValidationError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

def validate_credit_card(card_number):
    return re.match(r'^\d{16}$', card_number) is not None

def validate_phone(phone):
    return re.match(r'^\+?\d{1,15}$', phone) is not None

def mask_card_number(card_number):
    return f"{card_number[:4]}********{card_number[-4:]}"