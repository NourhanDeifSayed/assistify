from django.contrib import admin

from .models import (
    Conversation,
    InstagramWebhookEvent,
    Message,
)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = (
        "role",
        "content",
        "created_at",
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "session_key",
    )

    inlines = [
        MessageInline,
    ]


@admin.register(InstagramWebhookEvent)
class InstagramWebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message_id",
        "sender_id",
        "recipient_id",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "message_id",
        "sender_id",
        "recipient_id",
        "error",
    )

    readonly_fields = (
        "message_id",
        "sender_id",
        "recipient_id",
        "payload",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )