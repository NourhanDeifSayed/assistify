from django.contrib import admin
from .models import Conversation, Message, ConversationFeedback

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "created_at")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "created_at", "updated_at")
    inlines = [MessageInline]

@admin.register(ConversationFeedback)
class ConversationFeedbackAdmin(admin.ModelAdmin):
    list_display = (
    "id",
    "conversation",
    "rating",
    "user_email",
    "created_at",
    
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "conversation__user__email",
        "comment",
    )

    readonly_fields = (
        "conversation",
        "rating",
        "comment",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    @admin.display(description="Rating")
    def rating_label(self, obj):
        return obj.get_rating_display()

    @admin.display(description="User email")
    def user_email(self, obj):
        if obj.conversation.user:
            return obj.conversation.user.email
        return "-"