from django.contrib import admin
from .models import CreditCard, CreditCardPhoneAssociation

admin.site.register(CreditCard)
admin.site.register(CreditCardPhoneAssociation)