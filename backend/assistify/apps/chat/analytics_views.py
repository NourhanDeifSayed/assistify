from datetime import timedelta
from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
)
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from assistify.apps.chat.models import (
    Conversation,
    ConversationFeedback,
)
from assistify.apps.orders.models import Order, OrderItem
from assistify.apps.support.models import SupportTicket

class AnalyticsOverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        total_conversations = Conversation.objects.count()
        total_orders = Order.objects.count()
        total_tickets = SupportTicket.objects.count()
        total_feedback = ConversationFeedback.objects.count()

        average_rating = ConversationFeedback.objects.aggregate(
            average=Avg("rating"),
        )["average"]

        total_revenue = Order.objects.aggregate(
            total=Sum("total"),
        )["total"]

        orders_by_status = {
            item["status"]: item["count"]
            for item in Order.objects.values("status").annotate(
                count=Count("id"),
            ).order_by("status")
        }

        tickets_by_status = {
            item["status"]: item["count"]
            for item in SupportTicket.objects.values("status").annotate(
                count=Count("id"),
            ).order_by("status")
        }

        feedback_distribution = {
            str(item["rating"]): item["count"]
            for item in ConversationFeedback.objects.values(
                "rating",
            ).annotate(
                count=Count("id"),
            ).order_by("rating")
        }

        active_tickets = SupportTicket.objects.filter(
            status__in=[
                "open",
                "in_progress",
                "waiting_for_customer",
            ],
        ).count()

        resolved_tickets = SupportTicket.objects.filter(
            status__in=[
                "resolved",
                "closed",
            ],
        ).count()

        recent_conversations = Conversation.objects.filter(
            created_at__gte=thirty_days_ago,
        ).count()

        recent_orders = Order.objects.filter(
            created_at__gte=thirty_days_ago,
        ).count()

        recent_tickets = SupportTicket.objects.filter(
            created_at__gte=thirty_days_ago,
        ).count()

        conversations_with_orders = Conversation.objects.filter(
            order_id__isnull=False,
        ).count()

        conversion_rate = 0

        if total_conversations:
            conversion_rate = round(
                (
                    conversations_with_orders
                    / total_conversations
                )
                * 100,
                2,
            )

        seven_days_ago = now - timedelta(days=6)

        daily_conversations_query = (
            Conversation.objects.filter(
                created_at__date__gte=seven_days_ago.date(),
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        daily_orders_query = (
            Order.objects.filter(
                created_at__date__gte=seven_days_ago.date(),
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                count=Count("id"),
                revenue=Sum("total"),
            )
            .order_by("day")
        )

        daily_tickets_query = (
            SupportTicket.objects.filter(
                created_at__date__gte=seven_days_ago.date(),
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        conversation_map = {
            item["day"]: item["count"]
            for item in daily_conversations_query
        }

        order_map = {
            item["day"]: {
                "count": item["count"],
                "revenue": str(item["revenue"] or 0),
            }
            for item in daily_orders_query
        }

        ticket_map = {
            item["day"]: item["count"]
            for item in daily_tickets_query
        }

        daily_trends = []

        for offset in range(7):
            day = seven_days_ago.date() + timedelta(days=offset)
            order_data = order_map.get(
                day,
                {
                    "count": 0,
                    "revenue": "0",
                },
            )

            daily_trends.append(
                {
                    "date": day.isoformat(),
                    "conversations": conversation_map.get(day, 0),
                    "orders": order_data["count"],
                    "revenue": order_data["revenue"],
                    "tickets": ticket_map.get(day, 0),
                }
            )

        item_revenue_expression = ExpressionWrapper(
            F("unit_price") * F("quantity"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        top_products_query = (
            OrderItem.objects.values("product_name")
            .annotate(
                units_sold=Sum("quantity"),
                revenue=Sum(item_revenue_expression),
                orders_count=Count(
                    "order",
                    distinct=True,
                ),
            )
            .order_by(
                "-units_sold",
                "-revenue",
            )[:5]
        )

        top_products = [
            {
                "product": item["product_name"],
                "units_sold": item["units_sold"] or 0,
                "orders_count": item["orders_count"],
                "revenue": str(item["revenue"] or 0),
            }
            for item in top_products_query
        ]

        return Response(
            {
                "overview": {
                    "total_conversations": total_conversations,
                    "conversations_with_orders": conversations_with_orders,
                    "total_orders": total_orders,
                    "total_tickets": total_tickets,
                    "active_tickets": active_tickets,
                    "resolved_tickets": resolved_tickets,
                    "total_feedback": total_feedback,
                    "average_feedback_rating": (
                        round(average_rating, 2)
                        if average_rating is not None
                        else 0
                    ),
                    "total_revenue": str(total_revenue or 0),
                    "conversation_to_order_rate": conversion_rate,
                },
                "last_30_days": {
                    "conversations": recent_conversations,
                    "orders": recent_orders,
                    "tickets": recent_tickets,
                },
                "orders_by_status": orders_by_status,
                "tickets_by_status": tickets_by_status,
                "feedback_distribution": feedback_distribution,
                "daily_trends": daily_trends,
                "top_products": top_products,
            }
        )