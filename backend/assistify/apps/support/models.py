import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class SupportTicket(models.Model):
    class IssueType(models.TextChoices):
        DAMAGED_ITEM = "damaged_item", "Damaged Item"
        MISSING_ITEM = "missing_item", "Missing Item"
        DELAYED_ORDER = "delayed_order", "Delayed Order"
        WRONG_ITEM = "wrong_item", "Wrong Item"
        REFUND_REQUEST = "refund_request", "Refund Request"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_FOR_CUSTOMER = (
            "waiting_for_customer",
            "Waiting for Customer",
        )
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_tickets",
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_tickets",
    )

    conversation = models.ForeignKey(
        "chat.Conversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_tickets",
    )

    issue_type = models.CharField(
        max_length=30,
        choices=IssueType.choices,
        default=IssueType.OTHER,
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_support_tickets",
    )

    admin_response = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "support_tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            year = timezone.now().year
            unique_part = uuid.uuid4().hex[:12].upper()
            self.ticket_number = f"TKT-{year}-{unique_part}"

        completed_statuses = {
            self.Status.RESOLVED,
            self.Status.CLOSED,
        }

        if self.status in completed_statuses:
            if self.resolved_at is None:
                self.resolved_at = timezone.now()
        else:
            self.resolved_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} — {self.get_issue_type_display()}"


class FAQEntry(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=100)
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faq_entries"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.question