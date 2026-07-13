"""Signed webhook delivery.

Called from agent.py's shutdown callback once a call result has been saved
(and, if enabled, analyzed by Gemini). Builds the payload shape the client
expects, signs it, and POSTs it with retries. Never raises into the caller --
delivery failure is logged and swallowed so it can't crash call teardown.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

import httpx
import tenacity

from communication.config import config
from communication.logging.logger import logger

# Maps the agent's internal final_status values to the customer_response
# strings a client integration would actually want to branch on.
_STATUS_MAP = {
    "CONFIRMED": "confirmed",
    "CANCELLED": "cancelled",
    "CALLBACK_SCHEDULED": "callback_scheduled",
    "FAILED": "failed",
    "SILENT_NO_RESPONSE": "no_response",
    "CUSTOMER_HUNG_UP": "hung_up",
    "WRONG_NUMBER": "wrong_number",
    "DO_NOT_CALL": "do_not_call",
    "ESCALATION_REQUESTED": "escalation_requested",
    "UNKNOWN": "unknown",
}


def _sign(body: bytes) -> str:
    return hmac.new(config.WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()


def build_webhook_payload(call_data: dict[str, Any]) -> dict[str, Any]:
    """Map a saved call_results/*.json dict to the client-facing webhook shape."""
    final_status = call_data.get("final_status") or "UNKNOWN"
    transcript_list = call_data.get("transcript") or []
    transcript_text = "\n".join(
        f"{t.get('speaker', '').capitalize()}: {t.get('text', '')}" for t in transcript_list
    )
    analysis = call_data.get("conversation_analysis") or {}

    return {
        "request_id": call_data.get("request_id"),
        "call_id": call_data.get("call_id"),
        "call_status": "failed" if final_status == "FAILED" else "completed",
        "customer_response": _STATUS_MAP.get(final_status, final_status.lower()),
        "summary": analysis.get("summary") or "",
        "transcript": transcript_text,
        "call_duration": call_data.get("call_duration_seconds"),
    }


@tenacity.retry(
    stop=tenacity.stop_after_attempt(config.WEBHOOK_MAX_RETRIES),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def _post(callback_url: str, body: bytes, headers: dict[str, str]) -> None:
    async with httpx.AsyncClient(timeout=config.WEBHOOK_TIMEOUT_SECONDS) as client:
        response = await client.post(callback_url, content=body, headers=headers)
        response.raise_for_status()


async def send_webhook(callback_url: str, payload: dict[str, Any]) -> bool:
    """POST a signed payload to callback_url. Returns True on success, False otherwise."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature": _sign(body),
    }
    try:
        await _post(callback_url, body, headers)
        logger.info("Webhook delivered to %s (request_id=%s)", callback_url, payload.get("request_id"))
        return True
    except Exception as exc:
        logger.error(
            "Webhook delivery failed for %s after %d attempt(s): %s",
            callback_url,
            config.WEBHOOK_MAX_RETRIES,
            exc,
        )
        return False


async def deliver(result_path: Path, callback_url: str) -> bool:
    """Read a saved call result and send it to callback_url. Never raises."""
    try:
        call_data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Webhook: failed to read result file %s: %s", result_path, exc)
        return False

    payload = build_webhook_payload(call_data)
    return await send_webhook(callback_url, payload)
