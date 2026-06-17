from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SupportTicket
from .serializers import (
    SupportTicketCreateSerializer,
    SupportTicketDetailSerializer,
    SupportTicketReplySerializer,
    SupportTicketUpdateSerializer,
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

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)

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

        if ticket.assigned_to_id is None:
            ticket.assigned_to = request.user

        ticket.save()

        return Response(
            SupportTicketDetailSerializer(ticket).data,
            status=status.HTTP_200_OK,
        )