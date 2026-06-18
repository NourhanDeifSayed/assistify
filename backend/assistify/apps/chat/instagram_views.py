import hashlib
import hmac
import json
import logging
import os
import threading
from typing import Any

from django.conf import settings
from django.db import close_old_connections
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.views import APIView

from .instagram_client import (
    InstagramAPIError,
    send_sender_action,
    send_text_message,
)
from .models import (
    Conversation,
    InstagramWebhookEvent,
    Message,
)
from .service import get_chat_response


logger = logging.getLogger(__name__)


def _is_valid_signature(
    raw_body: bytes,
    received_signature: str,
) -> bool:
    """
    Verify that the webhook request was sent by Meta.
    """

    if not settings.INSTAGRAM_VERIFY_SIGNATURE:
        return True

    app_secret = os.getenv("INSTAGRAM_APP_SECRET", "")

    if not app_secret or not received_signature:
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            app_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(
        expected_signature,
        received_signature,
    )


def _extract_text(event: dict[str, Any]) -> str:
    """
    Extract text from an Instagram message, quick reply,
    postback or attachment.
    """

    message = event.get("message") or {}

    # Ignore messages sent by the chatbot itself.
    if message.get("is_echo"):
        return ""

    text = message.get("text")

    if text:
        return str(text).strip()

    quick_reply = message.get("quick_reply") or {}

    if quick_reply.get("payload"):
        return str(quick_reply["payload"]).strip()

    postback = event.get("postback") or {}

    if postback.get("payload"):
        return str(postback["payload"]).strip()

    attachments = message.get("attachments") or []

    if attachments:
        return "[Instagram attachment]"

    return ""


def _extract_message_id(
    event: dict[str, Any],
) -> str:
    """
    Extract the Meta message ID used to prevent duplicate replies.
    """

    message = event.get("message") or {}
    postback = event.get("postback") or {}

    message_id = (
        message.get("mid")
        or postback.get("mid")
        or ""
    )

    return str(message_id).strip()


def _extract_webhook_events(
    entry: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract events from both Instagram webhook payload formats.
    """

    events: list[dict[str, Any]] = []

    messaging_events = entry.get("messaging") or []

    if isinstance(messaging_events, list):
        for event in messaging_events:
            if isinstance(event, dict):
                events.append(event)

    changes = entry.get("changes") or []

    if isinstance(changes, list):
        for change in changes:
            if not isinstance(change, dict):
                continue

            if change.get("field") not in {
                "messages",
                "messaging_postbacks",
            }:
                continue

            value = change.get("value")

            if not isinstance(value, dict):
                continue

            nested_events = value.get("messaging")

            if isinstance(nested_events, list):
                for event in nested_events:
                    if isinstance(event, dict):
                        events.append(event)
            else:
                events.append(value)

    return events


def _get_instagram_conversation(
    sender_id: str,
    recipient_id: str,
) -> Conversation:
    """
    Get the latest conversation for this Instagram user,
    or create a new one.
    """

    session_key = (
        f"instagram:{recipient_id}:{sender_id}"
    )[:64]

    conversation = (
        Conversation.objects
        .filter(session_key=session_key)
        .order_by("-updated_at")
        .first()
    )

    if conversation is None:
        conversation = Conversation.objects.create(
            session_key=session_key,
        )

    return conversation


def _mark_event(
    record: InstagramWebhookEvent,
    status: str,
    error: str = "",
) -> None:
    """
    Update an Instagram webhook event status.
    """

    record.status = status
    record.error = error[:2000]

    record.save(
        update_fields=[
            "status",
            "error",
            "updated_at",
        ]
    )


def _process_event(event_id: int) -> None:
    """
    Process the message outside the webhook request so Meta
    receives an immediate HTTP 200 response.
    """

    close_old_connections()

    record = None
    typing_started = False

    try:
        record = InstagramWebhookEvent.objects.get(
            id=event_id
        )

        message_text = _extract_text(record.payload)

        if not message_text:
            _mark_event(
                record,
                InstagramWebhookEvent.Status.IGNORED,
            )
            return

        conversation = _get_instagram_conversation(
            sender_id=record.sender_id,
            recipient_id=record.recipient_id,
        )

        if message_text == "[Instagram attachment]":
            chatbot_message = (
                "The user sent an Instagram attachment "
                "without any accompanying text."
            )
        else:
            chatbot_message = message_text

        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=message_text,
        )

        send_sender_action(
            record.sender_id,
            "mark_seen",
        )

        send_sender_action(
            record.sender_id,
            "typing_on",
        )

        typing_started = True

        result = get_chat_response(
            chatbot_message,
            user_id=None,
            conversation_id=conversation.id,
        )

        reply = str(
            result.get("response")
            or (
                "عذرًا، لم أتمكن من معالجة رسالتك الآن. "
                "حاولي مرة أخرى."
            )
        ).strip()

        Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=reply,
        )

        send_text_message(
            recipient_id=record.sender_id,
            text=reply,
        )

        _mark_event(
            record,
            InstagramWebhookEvent.Status.PROCESSED,
        )

    except InstagramWebhookEvent.DoesNotExist:
        logger.error(
            "Instagram webhook event %s was not found.",
            event_id,
        )

    except InstagramAPIError as exc:
        logger.exception(
            "Instagram API error while processing event %s.",
            event_id,
        )

        if record is not None:
            _mark_event(
                record,
                InstagramWebhookEvent.Status.FAILED,
                str(exc),
            )

    except Exception as exc:
        logger.exception(
            "Unexpected Instagram webhook error for event %s.",
            event_id,
        )

        if record is not None:
            _mark_event(
                record,
                InstagramWebhookEvent.Status.FAILED,
                str(exc),
            )

    finally:
        if (
            typing_started
            and record is not None
        ):
            send_sender_action(
                record.sender_id,
                "typing_off",
            )

        close_old_connections()


@method_decorator(csrf_exempt, name="dispatch")
class InstagramWebhookView(APIView):
    """
    Instagram webhook verification and message receiver.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Handle Meta webhook verification.
        """

        mode = request.query_params.get(
            "hub.mode",
            "",
        )

        received_token = request.query_params.get(
            "hub.verify_token",
            "",
        )

        challenge = request.query_params.get(
            "hub.challenge",
            "",
        )

        configured_token = (
            settings.INSTAGRAM_VERIFY_TOKEN or ""
        )

        token_is_valid = (
            bool(configured_token)
            and hmac.compare_digest(
                received_token,
                configured_token,
            )
        )

        if (
            mode == "subscribe"
            and token_is_valid
        ):
            return HttpResponse(
                challenge,
                status=200,
                content_type="text/plain",
            )

        return HttpResponse(
            "Webhook verification failed",
            status=403,
            content_type="text/plain",
        )

    def post(self, request):
        """
        Receive incoming Instagram messaging events.
        """

        raw_body = request.body

        received_signature = request.headers.get(
            "X-Hub-Signature-256",
            "",
        )

        if not _is_valid_signature(
            raw_body,
            received_signature,
        ):
            return JsonResponse(
                {
                    "error": (
                        "Invalid webhook signature"
                    ),
                },
                status=403,
            )

        try:
            payload = json.loads(
                raw_body.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                },
                status=400,
            )

        if payload.get("object") != "instagram":
            return JsonResponse(
                {
                    "status": "ignored",
                    "reason": (
                        "Unsupported webhook object"
                    ),
                },
                status=200,
            )

        queued_events = 0

        entries = payload.get("entry") or []

        if not isinstance(entries, list):
            entries = []

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            account_id = str(
                entry.get("id") or ""
            )

            for event in _extract_webhook_events(entry):
                sender = event.get("sender") or {}
                recipient = (
                    event.get("recipient") or {}
                )

                sender_id = str(
                    sender.get("id") or ""
                )

                recipient_id = str(
                    recipient.get("id")
                    or account_id
                )

                if not sender_id:
                    continue

                message_id = _extract_message_id(
                    event
                )

                if message_id:
                    record, created = (
                        InstagramWebhookEvent
                        .objects
                        .get_or_create(
                            message_id=message_id,
                            defaults={
                                "sender_id": sender_id,
                                "recipient_id": (
                                    recipient_id
                                ),
                                "payload": event,
                            },
                        )
                    )

                    # Meta can retry the same webhook.
                    # Do not reply twice.
                    if not created:
                        continue

                else:
                    record = (
                        InstagramWebhookEvent
                        .objects
                        .create(
                            sender_id=sender_id,
                            recipient_id=recipient_id,
                            payload=event,
                        )
                    )

                worker = threading.Thread(
                    target=_process_event,
                    args=(record.id,),
                    daemon=True,
                )

                worker.start()
                queued_events += 1

        return JsonResponse(
            {
                "status": "accepted",
                "queued": queued_events,
            },
            status=200,
        )