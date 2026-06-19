from django.urls import path

from .views import (
    SupportTicketDetailUpdateView,
    SupportTicketListCreateView,
    SupportTicketReplyView,
    FAQListCreateView,
    FAQDetailView,
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
    path(
        "faq/",
        FAQListCreateView.as_view(),
        name="faq-list-create",
    ),
    path(
        "faq/<int:pk>/",
        FAQDetailView.as_view(),
        name="faq-detail",
    ),
]