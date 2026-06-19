from django.urls import path
from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    OfferListView,
    AdminOfferListCreateView,
    AdminOfferRetrieveUpdateDestroyView
)
app_name = "products"

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path("<int:pk>/", ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),
    path("offers/", OfferListView.as_view(), name="offer-list"),
    path("admin/offers/", AdminOfferListCreateView.as_view(), name="admin-offer-list"),
    path("admin/offers/<int:pk>/", AdminOfferRetrieveUpdateDestroyView.as_view(), name="admin-offer-detail"),
]