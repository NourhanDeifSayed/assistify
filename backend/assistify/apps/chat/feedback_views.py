from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistify.apps.chat.models import ConversationFeedback
from assistify.apps.chat.serializers import (
    ConversationFeedbackSerializer,
)


class ConversationFeedbackView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationFeedbackSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = ConversationFeedback.objects.select_related(
                "conversation",
                "conversation__user",
            ).all().order_by("-created_at")
        else:
            queryset = ConversationFeedback.objects.select_related(
                "conversation",
                "conversation__user",
            ).filter(
                conversation__user=user,
            ).order_by("-created_at")

        if user.is_staff:
            # Search
            search = self.request.query_params.get("search", "").strip()
            if search:
                from django.db import models
                queryset = queryset.filter(
                    models.Q(comment__icontains=search) |
                    models.Q(conversation__user__email__icontains=search) |
                    models.Q(conversation__user_name__icontains=search)
                )

            # Filter by rating
            rating = self.request.query_params.get("rating")
            if rating:
                queryset = queryset.filter(rating=rating)

            # Filter by user
            user_id = self.request.query_params.get("user")
            if user_id:
                queryset = queryset.filter(conversation__user_id=user_id)

        return queryset