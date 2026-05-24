from django.urls import path
from .views import decide_unsubscribe

urlpatterns = [
    path('decideUnsubscribe', decide_unsubscribe, name='decide_unsubscribe'),
]