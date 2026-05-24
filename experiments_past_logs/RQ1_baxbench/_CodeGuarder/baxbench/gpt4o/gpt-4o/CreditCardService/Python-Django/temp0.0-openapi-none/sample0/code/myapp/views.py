from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from .models import CreditCardAssociation
import json

@csrf_exempt
@require_POST
def associate_card(request):
    try:
        data = json.loads(request.body)
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        association, created = CreditCardAssociation.objects.get_or_create(
            credit_card=credit_card,
            phone=phone
        )

        if created:
            return JsonResponse({'message': 'Association created successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Association already exists'}, status=200)

    except (json.JSONDecodeError, ValidationError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@require_POST
def retrieve_cards(request):
    try:
        data = json.loads(request.body)
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        card_numbers = CreditCardAssociation.objects.filter(
            phone__in=phone_numbers
        ).values_list('credit_card', flat=True).distinct()

        if card_numbers:
            return JsonResponse({'card_numbers': list(card_numbers)}, status=200)
        else:
            return JsonResponse({'error': 'Not found'}, status=404)

    except (json.JSONDecodeError, ValidationError):
        return JsonResponse({'error': 'Invalid request'}, status=400)