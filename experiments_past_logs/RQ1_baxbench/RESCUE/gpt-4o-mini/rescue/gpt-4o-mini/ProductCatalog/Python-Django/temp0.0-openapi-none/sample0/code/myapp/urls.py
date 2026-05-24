from django.urls import path
from .views import ProductCatalogView, ProductUploadView, ProductSearchView

urlpatterns = [
    path('add', ProductCatalogView.as_view(), name='add_product'),
    path('download', ProductCatalogView.as_view(), name='download_product'),
    path('upload', ProductUploadView.as_view(), name='upload_product'),
    path('search', ProductSearchView.as_view(), name='search_product'),
]