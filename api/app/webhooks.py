import hashlib
import hmac
import json
import logging
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import WebhookOutbox

logger = logging.getLogger(__name__)


def sign_payload(payload: bytes) -> str:
    return hmac.new(
        settings.webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()


def add_to_outbox(db: Session, event_type: str, payload: dict) -> WebhookOutbox:
    event = WebhookOutbox(
        event_id=str(uuid4()),
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


async def deliver_outbox_event(db: Session, event: WebhookOutbox) -> None:
    body = json.dumps(
        {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "payload": event.payload,
        },
        separators=(",", ":"),
    ).encode()

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": sign_payload(body),
        "X-Event-Id": event.event_id,
    }

    event.attempts += 1

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.webhook_url, content=body, headers=headers)
            response.raise_for_status()

        event.delivered = True
        event.last_error = None
        logger.info("webhook_delivered", extra={"event_id": event.event_id})

    except Exception as exc:
        event.last_error = str(exc)
        logger.exception("webhook_delivery_failed", extra={"event_id": event.event_id})

    db.commit()