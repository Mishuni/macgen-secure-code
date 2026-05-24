from django.urls import path
from .views import entries, entry_detail, entry_edits

urlpatterns = [
    path('entries', entries, name='entries'),
    path('entries/<str:entryId>', entry_detail, name='entry_detail'),
    path('entries/<str:entryId>/edits', entry_edits, name='entry_edits'),
]