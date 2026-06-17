from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assistify.apps.chat.models import ConversationFeedback
from assistify.apps.chat.serializers import (
    ConversationFeedbackSerializer,
)


class ConversationFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            feedback = ConversationFeedback.objects.select_related(
                "conversation",
            ).all()
        else:
            feedback = ConversationFeedback.objects.select_related(
                "conversation",
            ).filter(
                conversation__user=request.user,
            )

        serializer = ConversationFeedbackSerializer(
            feedback,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ConversationFeedbackSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()

        response_serializer = ConversationFeedbackSerializer(
            feedback,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )