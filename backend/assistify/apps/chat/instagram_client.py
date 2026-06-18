import logging
from typing import Iterable

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class InstagramAPIError(RuntimeError):
    """Raised when Instagram rejects a Send API request."""


def _messages_endpoint() -> str:
    host = settings.INSTAGRAM_GRAPH_HOST.rstrip("/")
    version = settings.INSTAGRAM_API_VERSION.strip("/")

    return f"{host}/{version}/me/messages"


def _split_message(text: str, limit: int = 900) -> Iterable[str]:
    """
    Split long chatbot responses into smaller Instagram messages.
    """

    text = (text or "").strip()

    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)

        if split_at < limit // 2:
            split_at = text.rfind(" ", 0, limit)

        if split_at < limit // 2:
            split_at = limit

        part = text[:split_at].strip()

        if part:
            yield part

        text = text[split_at:].strip()

    if text:
        yield text


def send_text_message(recipient_id: str, text: str) -> list[dict]:
    """
    Send a text message from the Instagram professional account.
    """

    access_token = settings.INSTAGRAM_ACCESS_TOKEN

    if not access_token:
        raise InstagramAPIError(
            "INSTAGRAM_ACCESS_TOKEN is not configured."
        )

    if not recipient_id:
        raise InstagramAPIError(
            "Instagram recipient ID is missing."
        )

    results = []

    for part in _split_message(text):
        try:
            response = requests.post(
                _messages_endpoint(),
                params={
                    "access_token": access_token,
                },
                json={
                    "recipient": {
                        "id": recipient_id,
                    },
                    "message": {
                        "text": part,
                    },
                },
                timeout=20,
            )
        except requests.RequestException as exc:
            raise InstagramAPIError(
                f"Could not connect to Instagram API: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {
                "raw": response.text,
            }

        if not response.ok:
            logger.error(
                "Instagram Send API returned HTTP %s: %s",
                response.status_code,
                payload,
            )

            raise InstagramAPIError(
                f"Instagram returned HTTP "
                f"{response.status_code}: {payload}"
            )

        results.append(payload)

    return results


def send_sender_action(
    recipient_id: str,
    action: str,
) -> None:
    """
    Send actions such as mark_seen, typing_on or typing_off.
    """

    access_token = settings.INSTAGRAM_ACCESS_TOKEN

    if not access_token or not recipient_id:
        return

    try:
        response = requests.post(
            _messages_endpoint(),
            params={
                "access_token": access_token,
            },
            json={
                "recipient": {
                    "id": recipient_id,
                },
                "sender_action": action,
            },
            timeout=10,
        )

        if not response.ok:
            logger.warning(
                "Instagram sender action failed: HTTP %s - %s",
                response.status_code,
                response.text,
            )

    except requests.RequestException:
        logger.warning(
            "Could not send Instagram sender action.",
            exc_info=True,
        )
        