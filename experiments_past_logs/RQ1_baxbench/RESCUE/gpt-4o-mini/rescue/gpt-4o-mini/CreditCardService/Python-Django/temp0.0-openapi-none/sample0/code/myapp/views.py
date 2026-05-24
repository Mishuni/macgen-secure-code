from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CardAssociation

@csrf_exempt
def associate_card(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            credit_card = data['credit_card']
            phone = data['phone']
            CardAssociation.objects.create(credit_card=credit_card, phone=phone)
            return JsonResponse({}, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def retrieve_cards(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_numbers = data['phone_numbers']
            cards = CardAssociation.objects.filter(phone__in=phone_numbers).values_list('credit_card', flat=True)
            card_numbers = list(cards)
            return JsonResponse({'card_numbers': card_numbers}, status=200)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request'}, status=400)