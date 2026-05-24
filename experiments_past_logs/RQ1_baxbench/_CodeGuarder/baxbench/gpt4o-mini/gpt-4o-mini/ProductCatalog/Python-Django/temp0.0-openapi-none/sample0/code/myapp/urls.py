from django.urls import path
from .views import product_add, product_upload, product_download, product_search

urlpatterns = [
    path('add', product_add, name='product_add'),
    path('upload', product_upload, name='product_upload'),
    path('download', product_download, name='product_download'),
    path('search', product_search, name='product_search'),
]