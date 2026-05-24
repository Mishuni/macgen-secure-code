from django.urls import path
from .views import EntryView

urlpatterns = [
    path('', EntryView.as_view()),
    path('<int:entry_id>', EntryView.as_view()),
]