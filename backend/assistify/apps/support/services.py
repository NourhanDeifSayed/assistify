from django.db import transaction

from assistify.apps.orders.models import Order

from .models import SupportTicket

import re

ISSUE_KEYWORDS = {
    SupportTicket.IssueType.DAMAGED_ITEM: (
        "تالف",
        "مكسور",
        "بايظ",
        "مش شغال",
        "damaged",
        "broken",
        "defective",
        "not working",
    ),
    SupportTicket.IssueType.MISSING_ITEM: (
        "ناقص",
        "مش موجود",
        "مفقود",
        "missing item",
        "item missing",
        "not included",
    ),
    SupportTicket.IssueType.DELAYED_ORDER: (
        "الطلب متأخر",
        "اتأخر",
        "متأخر جدًا",
        "delayed order",
        "order is late",
        "late delivery",
    ),
    SupportTicket.IssueType.WRONG_ITEM: (
        "منتج غلط",
        "منتج مختلف",
        "وصلني غيره",
        "wrong item",
        "different product",
    ),
    SupportTicket.IssueType.REFUND_REQUEST: (
        "استرجاع",
        "ارجاع",
        "استرداد",
        "refund",
        "return product",
        "money back",
    ),
    SupportTicket.IssueType.OTHER: (
        "عايز أكلم موظف",
        "عاوز اكلم موظف",
        "خدمة العملاء",
        "موظف بشري",
        "human agent",
        "customer support",
        "speak to an agent",
    ),
}


URGENT_KEYWORDS = (
    "خطر",
    "إصابة",
    "اصابة",
    "طارئ",
    "urgent",
    "dangerous",
    "injury",
    "unsafe",
)


def detect_issue_type(message):
    normalized_message = str(message or "").strip().lower()

    if not normalized_message:
        return None

    for issue_type, keywords in ISSUE_KEYWORDS.items():
        if any(keyword in normalized_message for keyword in keywords):
            return issue_type

    return None


def determine_priority(message, issue_type):
    normalized_message = str(message or "").strip().lower()

    if any(keyword in normalized_message for keyword in URGENT_KEYWORDS):
        return SupportTicket.Priority.URGENT

    if issue_type in {
        SupportTicket.IssueType.DAMAGED_ITEM,
        SupportTicket.IssueType.MISSING_ITEM,
        SupportTicket.IssueType.WRONG_ITEM,
        SupportTicket.IssueType.REFUND_REQUEST,
    }:
        return SupportTicket.Priority.HIGH

    if issue_type == SupportTicket.IssueType.DELAYED_ORDER:
        return SupportTicket.Priority.MEDIUM

    return SupportTicket.Priority.MEDIUM


def get_latest_order_for_user(user):
    if not user or not user.is_authenticated:
        return None

    return (
        Order.objects.filter(user=user)
        .order_by("-id")
        .first()
    )


@transaction.atomic
def create_support_ticket(
    *,
    user,
    conversation,
    order,
    issue_type,
    description,
    priority=None,
):
    description = str(description or "").strip()

    if not description:
        raise ValueError("Ticket description cannot be empty.")

    if priority is None:
        priority = determine_priority(description, issue_type)

    active_statuses = (
        SupportTicket.Status.OPEN,
        SupportTicket.Status.IN_PROGRESS,
        SupportTicket.Status.WAITING_FOR_CUSTOMER,
    )

    existing_ticket = (
        SupportTicket.objects.filter(
            user=user,
            order=order,
            issue_type=issue_type,
            status__in=active_statuses,
        )
        .order_by("-id")
        .first()
    )

    if existing_ticket:
        return existing_ticket, False

    ticket = SupportTicket.objects.create(
        user=user,
        conversation=conversation,
        order=order,
        issue_type=issue_type,
        description=description,
        priority=priority,
        status=SupportTicket.Status.OPEN,
    )

    return ticket, True

TICKET_TRACKING_KEYWORDS = (
    "فين شكوتي",
    "حالة شكوتي",
    "تابع الشكوى",
    "متابعة الشكوى",
    "فين التذكرة",
    "حالة التذكرة",
    "شكوتي وصلت لفين",
    "track my complaint",
    "complaint status",
    "ticket status",
    "where is my ticket",
)

TICKET_NUMBER_PATTERN = re.compile(
    r"\btkt-\d{4}-[a-z0-9]{6,50}\b",
    re.IGNORECASE,
)


def is_ticket_tracking_request(message):
    normalized_message = str(message or "").strip().lower()

    if not normalized_message:
        return False

    if TICKET_NUMBER_PATTERN.search(normalized_message):
        return True

    return any(
        keyword in normalized_message
        for keyword in TICKET_TRACKING_KEYWORDS
    )


def extract_ticket_number(message):
    match = TICKET_NUMBER_PATTERN.search(
        str(message or "").strip()
    )

    if not match:
        return None

    return match.group(0).upper()


def get_ticket_for_user(user, ticket_number=None):
    if not user or not getattr(user, "pk", None):
        return None

    queryset = SupportTicket.objects.filter(
        user=user,
    ).select_related(
        "order",
        "conversation",
        "assigned_to",
    )

    if ticket_number:
        return queryset.filter(
            ticket_number__iexact=ticket_number,
        ).first()

    return queryset.order_by("-created_at").first()