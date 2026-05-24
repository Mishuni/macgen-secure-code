from django.urls import path
from . import views

urlpatterns = [
    path('add', views.add_product, name='add_product'),
    path('download', views.download_catalog, name='download_catalog'),
    path('upload', views.upload_catalog, name='upload_catalog'),
    path('search', views.search_products, name='search_products'),
]