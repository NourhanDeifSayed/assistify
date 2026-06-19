from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SupportTicket, FAQEntry
from .serializers import (
    SupportTicketCreateSerializer,
    SupportTicketDetailSerializer,
    SupportTicketReplySerializer,
    SupportTicketUpdateSerializer,
    FAQEntrySerializer,
)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

class SupportTicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SupportTicket.objects.select_related(
            "user",
            "order",
            "conversation",
            "assigned_to",
        )

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            # For admin, support user filter
            user_id = self.request.query_params.get("user")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        # Advanced Search (ticket_number, email, description)
        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db import models
            queryset = queryset.filter(
                models.Q(ticket_number__icontains=search) |
                models.Q(user__email__icontains=search) |
                models.Q(description__icontains=search)
            )

        # Filters: status, priority, category (issue_type), dates
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(issue_type=category)

        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Sorting
        ordering = self.request.query_params.get("ordering", "-created_at")
        allowed_ordering = ["created_at", "-created_at", "updated_at", "-updated_at", "priority", "-priority", "status", "-status"]
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupportTicketCreateSerializer

        return SupportTicketDetailSerializer


class SupportTicketDetailUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "ticket_number"
    http_method_names = ["get", "patch", "options"]

    def get_queryset(self):
        queryset = SupportTicket.objects.select_related(
            "user",
            "order",
            "conversation",
            "assigned_to",
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return SupportTicketUpdateSerializer

        return SupportTicketDetailSerializer

    def patch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":
                        "Only staff members can update support tickets."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().patch(request, *args, **kwargs)

        ticket = self.get_object()

        return Response(
            SupportTicketDetailSerializer(ticket).data,
            status=response.status_code,
        )


class SupportTicketReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_number):
        if not request.user.is_staff:
            return Response(
                {
                    "detail":
                        "Only staff members can reply to support tickets."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        ticket = get_object_or_404(
            SupportTicket,
            ticket_number=ticket_number,
        )

        serializer = SupportTicketReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket.admin_response = serializer.validated_data["response"]

        new_status = serializer.validated_data.get("status")

        if new_status:
            ticket.status = new_status
        elif ticket.status == SupportTicket.Status.OPEN:
            ticket.status = SupportTicket.Status.IN_PROGRESS

        # Always set assigned_to to current admin if not set
        if ticket.assigned_to_id is None:
            ticket.assigned_to = request.user
        elif serializer.validated_data.get("status") == SupportTicket.Status.RESOLVED:
            ticket.assigned_to = request.user

        ticket.save()

        return Response(
            SupportTicketDetailSerializer(ticket).data,
            status=status.HTTP_200_OK,
        )


class FAQListCreateView(generics.ListCreateAPIView):
    serializer_class = FAQEntrySerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        is_admin = user and user.is_authenticated and (
            user.is_superuser
            or user.is_staff
            or user.role == "admin"
            or getattr(user, "is_admin_user", False)
        )

        if is_admin:
            queryset = FAQEntry.objects.all()
        else:
            queryset = FAQEntry.objects.filter(is_published=True)

        # Search
        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db import models
            queryset = queryset.filter(
                models.Q(question__icontains=search) |
                models.Q(answer__icontains=search) |
                models.Q(keywords__icontains=search)
            )

        # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        # Filter by published status for admins
        if is_admin:
            is_published = self.request.query_params.get("is_published")
            if is_published in ("true", "false"):
                queryset = queryset.filter(is_published=(is_published == "true"))

        return queryset


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQEntry.objects.all()
    serializer_class = FAQEntrySerializer
    permission_classes = [IsAdminUserOrReadOnly]