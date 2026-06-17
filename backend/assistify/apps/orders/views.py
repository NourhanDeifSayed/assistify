from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, TrackingUpdate
from .serializers import (
    GuestOrderTrackingInputSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    OrderTrackingSerializer,
    PlaceOrderSerializer,
    ReviewSerializer,
)

ORDER_TRACKING_TOKEN_SALT = "assistify.order.tracking"
ORDER_TRACKING_TOKEN_MAX_AGE = 60 * 60 * 24 * 180

def generate_order_tracking_token(order):
    return signing.dumps(
        {
            "order_number": order.order_number,
        },
        salt=ORDER_TRACKING_TOKEN_SALT,
        compress=True,
    )

def user_is_admin(user):
    if not user or not user.is_authenticated:
        return False
    return bool(
        user.is_superuser
        or user.is_staff
        or getattr(user, "is_admin_user", False)
    )

class IsAdminUser(permissions.BasePermission):
    message = "Admin access is required."

    def has_permission(self, request, view):
        return user_is_admin(request.user)

class PlaceOrderView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = PlaceOrderSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )
        save_data = {}
        if request.user.is_authenticated:
            save_data["user"] = request.user
        order = serializer.save(
            **save_data,
        )
        tracking_token = generate_order_tracking_token(
            order,
        )
        return Response(
            {
                "message": "Order placed successfully.",
                "order": OrderSerializer(order).data,
                "tracking_token": tracking_token,
            },
            status=status.HTTP_201_CREATED,
        )

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items",
                "tracking_updates",
            )
        )
        user = self.request.user
        if user_is_admin(user):
            return queryset.all()
        return queryset.filter(
            user=user,
        )

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    lookup_field = "order_number"
    lookup_url_kwarg = "order_number"

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items",
                "tracking_updates",
            )
        )
        user = self.request.user
        if user_is_admin(user):
            return queryset.all()
        return queryset.filter(
            user=user,
        )

class GuestOrderTrackingView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = GuestOrderTrackingInputSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        order_number = serializer.validated_data[
            "order_number"
        ]
        tracking_token = serializer.validated_data[
            "tracking_token"
        ]
        try:
            token_payload = signing.loads(
                tracking_token,
                salt=ORDER_TRACKING_TOKEN_SALT,
                max_age=ORDER_TRACKING_TOKEN_MAX_AGE,
            )
        except (BadSignature, SignatureExpired):
            return self.invalid_tracking_response()
        token_order_number = token_payload.get(
            "order_number"
        )
        if token_order_number != order_number:
            return self.invalid_tracking_response()
        try:
            order = (
                Order.objects
                .prefetch_related(
                    "items",
                    "tracking_updates",
                )
                .get(
                    order_number=order_number,
                )
            )
        except Order.DoesNotExist:
            return self.invalid_tracking_response()
        return Response(
            {
                "order": OrderTrackingSerializer(
                    order,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def invalid_tracking_response():
        return Response(
            {
                "detail": (
                    "Invalid or expired tracking credentials."
                ),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

class OrderStatusUpdateView(APIView):
    permission_classes = [
        IsAdminUser,
    ]

    @transaction.atomic
    def patch(self, request, order_number):
        try:
            order = (
                Order.objects
                .select_for_update()
                .get(
                    order_number=order_number,
                )
            )
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={
                "order": order,
                "request": request,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )
        new_status = serializer.validated_data[
            "status"
        ]
        location = serializer.validated_data[
            "location"
        ]
        tracking_number = serializer.validated_data.get(
            "tracking_number",
            "",
        )
        order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        order.save()
        TrackingUpdate.objects.create(
            order=order,
            date=timezone.now().date(),
            status=order.get_status_display(),
            location=location,
        )
        updated_order = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items",
                "tracking_updates",
            )
            .get(pk=order.pk)
        )
        return Response(
            {
                "message": "Order status updated successfully.",
                "order": OrderSerializer(
                    updated_order,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )