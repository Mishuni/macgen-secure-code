from django.urls import path
from .views import EntryView, EntryDetailView

urlpatterns = [
    path('', EntryView.as_view(), name='entry-list'),
    path('<str:entryId>/', EntryDetailView.as_view(), name='entry-detail'),
]