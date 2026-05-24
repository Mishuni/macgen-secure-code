from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .models import CreditCard, CreditCardPhoneAssociation

class AssociateCardView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            credit_card_number = data.get("credit_card")
            phone = data.get("phone")

            if not credit_card_number or not phone:
                return JsonResponse({"error": "Invalid request"}, status=400)

            credit_card, _ = CreditCard.objects.get_or_create(number=credit_card_number)
            CreditCardPhoneAssociation.objects.get_or_create(credit_card=credit_card, phone=phone)

            return JsonResponse({"message": "Association created successfully"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class RetrieveCardsView(View):
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone_numbers = data.get("phone_numbers")

            if not phone_numbers or not isinstance(phone_numbers, list):
                return JsonResponse({"error": "Invalid request"}, status=400)

            cards = CreditCard.objects.filter(
                id__in=CreditCardPhoneAssociation.objects.filter(phone__in=phone_numbers)
                .values("credit_card")
                .annotate(count=models.Count("credit_card"))
                .filter(count=len(phone_numbers))
                .values("credit_card")
            )

            card_numbers = [card.number for card in cards]
            if not card_numbers:
                return JsonResponse({"error": "Not found"}, status=404)

            return JsonResponse({"card_numbers": card_numbers}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)