from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count
import json
from .models import CreditCardAssociation

@csrf_exempt
@require_POST
def associate_card(request):
    try:
        data = json.loads(request.body)
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        # Validate credit card and phone format
        if not credit_card.isdigit() or len(credit_card) != 16:
            return JsonResponse({'error': 'Invalid credit card format'}, status=400)
        if not phone.replace('-', '').isdigit() or len(phone.split('-')) != 3:
            return JsonResponse({'error': 'Invalid phone format'}, status=400)

        CreditCardAssociation.objects.create(credit_card=credit_card, phone=phone)
        return JsonResponse({'message': 'Association created successfully'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_POST
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

        return JsonResponse({'card_numbers': list(card_numbers)}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)