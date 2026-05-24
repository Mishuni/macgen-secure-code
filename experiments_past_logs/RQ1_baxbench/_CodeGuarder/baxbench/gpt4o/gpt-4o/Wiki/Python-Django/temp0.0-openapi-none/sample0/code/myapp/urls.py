from django.urls import path
from . import views

urlpatterns = [
    path('entries', views.list_entries, name='list_entries'),
    path('entries', views.create_entry, name='create_entry'),
    path('entries/<str:entry_id>', views.get_entry, name='get_entry'),
    path('entries/<str:entry_id>', views.update_entry, name='update_entry'),
    path('entries/<str:entry_id>/edits', views.entry_edits, name='entry_edits'),
]