from django.urls import path

from .views import (
    SupportTicketDetailUpdateView,
    SupportTicketListCreateView,
    SupportTicketReplyView,
)

app_name = "support"

urlpatterns = [
    path(
        "tickets/",
        SupportTicketListCreateView.as_view(),
        name="ticket-list-create",
    ),
    path(
        "tickets/<str:ticket_number>/",
        SupportTicketDetailUpdateView.as_view(),
        name="ticket-detail-update",
    ),
    path(
        "tickets/<str:ticket_number>/reply/",
        SupportTicketReplyView.as_view(),
        name="ticket-reply",
    ),
]