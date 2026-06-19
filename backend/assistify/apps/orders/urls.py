from django.urls import path
from .views import (
    GuestOrderTrackingView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
    PlaceOrderView,
    ReviewCreateView,
    AdminReviewListView,
)

app_name = "orders"

urlpatterns = [
    path(
        "reviews/admin/",
        AdminReviewListView.as_view(),
        name="admin-review-list",
    ),
    path(
        "",
        PlaceOrderView.as_view(),
        name="order-place",
    ),
    path(
        "list/",
        OrderListView.as_view(),
        name="order-list",
    ),
    path(
        "track/",
        GuestOrderTrackingView.as_view(),
        name="order-track",
    ),
    path(
        "reviews/create/",
        ReviewCreateView.as_view(),
        name="review-create",
    ),
    path(
        "<str:order_number>/status/",
        OrderStatusUpdateView.as_view(),
        name="order-status-update",
    ),
    path(
        "<str:order_number>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
]