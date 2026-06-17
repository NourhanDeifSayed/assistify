from django.contrib import admin

from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "issue_type",
        "status",
        "priority",
        "user",
        "order",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "issue_type",
        "status",
        "priority",
        "created_at",
    )

    search_fields = (
        "ticket_number",
        "description",
        "admin_response",
        "user__email",
        "order__order_number",
    )

    readonly_fields = (
        "ticket_number",
        "created_at",
        "updated_at",
        "resolved_at",
    )

    autocomplete_fields = (
    "user",
    "order",
    "assigned_to",
    )
    raw_id_fields = (
    "conversation",
    )

    ordering = ("-created_at",)