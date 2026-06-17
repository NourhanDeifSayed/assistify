import logging
import threading
from decouple import config
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Conversation, Message
from .service import get_chat_response

logger = logging.getLogger(__name__)

CONVERSATION_TOKEN_SALT = "assistify.conversation.access"
CONVERSATION_TOKEN_MAX_AGE = 60 * 60 * 24 * 180

def generate_conversation_token(conversation):
    return signing.dumps(
        {
            "conversation_id": conversation.id,
        },
        salt=CONVERSATION_TOKEN_SALT,
        compress=True,
    )

def conversation_token_is_valid(conversation, token):
    if not token:
        return False
    try:
        payload = signing.loads(
            token,
            salt=CONVERSATION_TOKEN_SALT,
            max_age=CONVERSATION_TOKEN_MAX_AGE,
        )
    except (BadSignature, SignatureExpired):
        return False
    return payload.get("conversation_id") == conversation.id

def user_is_admin(user):
    if not user or not user.is_authenticated:
        return False
    return bool(
        user.is_superuser
        or user.is_staff
        or getattr(user, "is_admin_user", False)
    )

def user_can_access_conversation(
    request,
    conversation,
    conversation_token=None,
    claim_guest_conversation=False,
):
    user = request.user
    if user.is_authenticated:
        if user_is_admin(user):
            return True
        if conversation.user_id == user.id:
            return True
        if (
            claim_guest_conversation
            and conversation.user_id is None
            and conversation_token_is_valid(
                conversation,
                conversation_token,
            )
        ):
            conversation.user = user
            conversation.save(
                update_fields=[
                    "user",
                    "updated_at",
                ]
            )
            return True
        return False
    return (
        conversation.user_id is None
        and conversation_token_is_valid(
            conversation,
            conversation_token,
        )
    )

class ChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message_text = request.data.get(
            "message",
            "",
        ).strip()
        conversation_id = request.data.get(
            "conversation_id"
        )
        conversation_token = request.data.get(
            "conversation_token"
        )
        if not message_text:
            return Response(
                {
                    "error": "message is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        conversation = self._get_or_create_conversation(
            request=request,
            conversation_id=conversation_id,
            conversation_token=conversation_token,
        )
        if request.user.is_authenticated and conversation.user_id is None:
            conversation.user = request.user
            conversation.save(update_fields=["user"])
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=message_text,
        )
        user_id = (
            request.user.id
            if request.user.is_authenticated
            else conversation.user_id
        )
        result = get_chat_response(
            message_text,
            user_id=user_id,
            conversation_id=conversation.id,
        )
        assistant_response = result.get(
            "response",
            "",
        )
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=assistant_response,
        )
        response_data = {
            "success": result.get(
                "success",
                True,
            ),
            "response": assistant_response,
            "reply": assistant_response,
            "message": assistant_response,
            "intent": result.get("intent"),
            "sentiment": result.get("sentiment"),
            "recommendations": result.get(
                "recommendations",
                [],
            ),
            "confidence": result.get(
                "confidence",
                {
                    "intent": 0.0,
                    "sentiment": 0.0,
                },
            ),
            "metadata": result.get(
                "metadata",
                {
                    "recommendation_method": "none",
                    "user_name": None,
                },
            ),
            "conversation_id": conversation.id,
            "conversation_token": (
                generate_conversation_token(
                    conversation
                )
            ),
        }
        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )

    def _get_or_create_conversation(
        self,
        request,
        conversation_id,
        conversation_token,
    ):
        if conversation_id is not None:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id
                )
            except (
                Conversation.DoesNotExist,
                ValueError,
                TypeError,
            ):
                raise NotFound(
                    "Conversation not found."
                )
            allowed = user_can_access_conversation(
                request=request,
                conversation=conversation,
                conversation_token=conversation_token,
                claim_guest_conversation=True,
            )
            if not allowed:
                raise NotFound(
                    "Conversation not found."
                )
            return conversation
        user = (
            request.user
            if request.user.is_authenticated
            else None
        )
        if not request.session.session_key:
            request.session.create()
        return Conversation.objects.create(
            user=user,
            session_key=(
                request.session.session_key or ""
            ),
        )

class ConversationHistoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, conversation_id):
        try:
            conversation = (
                Conversation.objects
                .prefetch_related("messages")
                .get(id=conversation_id)
            )
        except Conversation.DoesNotExist:
            raise NotFound(
                "Conversation not found."
            )
        conversation_token = (
            request.headers.get(
                "X-Conversation-Token"
            )
            or request.query_params.get(
                "conversation_token"
            )
        )
        allowed = user_can_access_conversation(
            request=request,
            conversation=conversation,
            conversation_token=conversation_token,
        )
        if not allowed:
            raise NotFound(
                "Conversation not found."
            )
        messages = [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in conversation.messages.all()
        ]
        return Response(
            {
                "conversation_id": conversation.id,
                "messages": messages,
            },
            status=status.HTTP_200_OK,
        )

class WhatsAppWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message_text = request.data.get(
            "Body",
            "",
        ).strip()
        sender = request.data.get(
            "From",
            "",
        )
        if not message_text or not sender:
            return HttpResponse(
                "Missing Body or From",
                status=400,
            )
        phone_number = sender.replace(
            "whatsapp:",
            "",
        ).strip()
        conversation, _ = (
            Conversation.objects.get_or_create(
                session_key=phone_number
            )
        )
        if not conversation.phone:
            conversation.phone = phone_number
            conversation.save(
                update_fields=[
                    "phone",
                    "updated_at",
                ]
            )
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=message_text,
        )
        thread = threading.Thread(
            target=self.process_and_reply,
            args=(
                message_text,
                sender,
                conversation.id,
            ),
            daemon=True,
        )
        thread.start()
        response = MessagingResponse()
        return HttpResponse(
            str(response),
            content_type="text/xml",
        )

    def process_and_reply(
        self,
        message_text,
        sender,
        conversation_id,
    ):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id
            )
            result = get_chat_response(
                message_text,
                user_id=None,
                conversation_id=conversation.id,
            )
            reply_text = result.get(
                "response",
                (
                    "عذرًا، أواجه مشكلة في معالجة "
                    "طلبك الآن."
                ),
            )
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=reply_text,
            )
            account_sid = config(
                "TWILIO_ACCOUNT_SID",
                default="",
            )
            auth_token = config(
                "TWILIO_AUTH_TOKEN",
                default="",
            )
            twilio_number = config(
                "TWILIO_WHATSAPP_NUMBER",
                default="+14155238886",
            )
            if not twilio_number.startswith(
                "whatsapp:"
            ):
                twilio_number = (
                    f"whatsapp:{twilio_number}"
                )
            if account_sid and auth_token:
                client = Client(
                    account_sid,
                    auth_token,
                )
                client.messages.create(
                    body=reply_text,
                    from_=twilio_number,
                    to=sender,
                )
            else:
                logger.error(
                    "Twilio credentials are missing. "
                    "WhatsApp reply was not sent."
                )
        except Exception as exc:
            logger.error(
                "WhatsApp background pipeline error: %s",
                exc,
                exc_info=True,
            )