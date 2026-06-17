from django.db import models
from django.conf import settings

class Conversation(models.Model):
    class ComplaintState(models.TextChoices):
        IDLE = "idle", "Idle"
        AWAITING_ORDER_CONFIRMATION = (
            "awaiting_order_confirmation",
            "Awaiting Order Confirmation",
        )
        AWAITING_DESCRIPTION = (
            "awaiting_description",
            "Awaiting Description",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    session_key = models.CharField(max_length=64, blank=True)
    last_product_id = models.IntegerField(null=True, blank=True)
    last_product_data = models.JSONField(null=True, blank=True)
    last_intent = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=10, default="en")
    user_name = models.CharField(max_length=100, null=True, blank=True)
    purchase_state = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Current step in purchase flow (e.g., 'awaiting_address')",
    )
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(null=True, blank=True)
    order_id = models.IntegerField(null=True, blank=True)
    complaint_state = models.CharField(
        max_length=40,
        choices=ComplaintState.choices,
        default=ComplaintState.IDLE,
    )
    complaint_issue_type = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )
    complaint_order_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )
    complaint_ticket = models.ForeignKey(
        "support.SupportTicket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        identifier = self.user.email if self.user else self.session_key
        return f"Conversation {self.id} — {identifier}"

class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"

class ConversationFeedback(models.Model):
    class Rating(models.IntegerChoices):
        VERY_BAD = 1, "Very Bad"
        BAD = 2, "Bad"
        AVERAGE = 3, "Average"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    rating = models.PositiveSmallIntegerField(
        choices=Rating.choices,
    )

    comment = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Conversation Feedback"
        verbose_name_plural = "Conversation Feedback"

    def __str__(self):
        return (
            f"Conversation {self.conversation_id} "
            f"- Rating {self.rating}/5"
        )