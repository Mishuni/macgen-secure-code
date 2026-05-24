from django.urls import path
from . import views

urlpatterns = [
    path('', views.entries_list),
    path('<str:entryId>', views.entry_detail),
    path('<str:entryId>/edits', views.entry_edits),
]