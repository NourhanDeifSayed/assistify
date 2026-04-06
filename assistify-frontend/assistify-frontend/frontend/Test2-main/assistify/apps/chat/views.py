import json

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .service import get_reply


class ChatView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message_text = request.data.get("message", "").strip()
        conversation_id = request.data.get("conversation_id")

        if not message_text:
            return Response({"error": "message is required."}, status=status.HTTP_400_BAD_REQUEST)

        conversation = self._get_or_create_conversation(request, conversation_id)

        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=message_text)

        reply = get_reply(message_text)

        Message.objects.create(conversation=conversation, role=Message.Role.ASSISTANT, content=reply)

        return Response({"reply": reply, "conversation_id": conversation.id})

    def _get_or_create_conversation(self, request, conversation_id):
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                pass
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ""
        return Conversation.objects.create(user=user, session_key=session_key)


class ConversationHistoryView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.prefetch_related("messages").get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = [
            {"role": m.role, "content": m.content, "created_at": m.created_at}
            for m in conversation.messages.all()
        ]
        return Response({"conversation_id": conversation.id, "messages": messages})
