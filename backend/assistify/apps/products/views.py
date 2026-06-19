from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Offer
from .serializers import ProductSerializer, ProductWriteSerializer, OfferSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductWriteSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        is_admin = user and user.is_authenticated and (
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

        if is_admin:
            queryset = Product.objects.all().prefetch_related("benefits", "related_products")
        else:
            queryset = Product.objects.filter(is_active=True).prefetch_related("benefits", "related_products")

        # Search by name, id, or category
        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db import models
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(category__icontains=search) |
                models.Q(id__iexact=search)
            )

        # Filters: category, active status, stock status, price range
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        is_active = self.request.query_params.get("is_active")
        if is_active in ("true", "false"):
            queryset = queryset.filter(is_active=(is_active == "true"))

        stock_status = self.request.query_params.get("stock_status")
        if stock_status == "instock":
            queryset = queryset.filter(stock__gt=0)
        elif stock_status == "outofstock":
            queryset = queryset.filter(stock__lte=0)

        min_price = self.request.query_params.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Sorting
        ordering = self.request.query_params.get("ordering", "id")
        allowed_ordering = ["id", "-id", "name", "-name", "price", "-price", "stock", "-stock", "created_at", "-created_at"]
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related("benefits", "related_products")
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProductWriteSerializer
        return ProductSerializer

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response({"message": "Product deactivated."})

class OfferListView(generics.ListAPIView):
    queryset = Offer.objects.filter(is_active=True).select_related("product")
    serializer_class = OfferSerializer
    permission_classes = [permissions.AllowAny]

class AdminOfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().select_related("product")
    serializer_class = OfferSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Offer.objects.all().select_related("product")
        
        # Search
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(product__name__icontains=search)
            
        # Filters
        is_active = self.request.query_params.get("is_active")
        if is_active in ("true", "false"):
            queryset = queryset.filter(is_active=(is_active == "true"))
            
        return queryset

class AdminOfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all().select_related("product")
    serializer_class = OfferSerializer
    permission_classes = [IsAdminUser]