from django.urls import path
from .views import entry_list, entry_detail

urlpatterns = [
    path('', entry_list, name='entry_list'),
    path('<str:entryId>/', entry_detail, name='entry_detail'),
]