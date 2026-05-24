from django.contrib import admin
from .models import CreditCardPhoneAssociation

@admin.register(CreditCardPhoneAssociation)
class CreditCardPhoneAssociationAdmin(admin.ModelAdmin):
    list_display = ('credit_card', 'phone')