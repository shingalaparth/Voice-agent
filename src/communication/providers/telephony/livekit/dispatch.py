"""Shared LiveKit dispatch logic.

Both the CLI (make_call.py) and the HTTP API (main.py) need to do the exact
same thing: build a unique room name, attach the customer record as job
metadata, and ask LiveKit to dispatch the 'outbound-caller' agent into that
room. Keeping it in one place means a trunk/room-naming fix only has to
happen once.
"""
from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass

from livekit import api

from communication.config import config
from communication.logging.logger import logger


class DispatchError(RuntimeError):
    """Raised when a call could not be dispatched (bad config or LiveKit API error)."""


@dataclass
class DispatchResult:
    dispatch_id: str
    room_name: str
    call_id: str


def _room_name_for(call_id: str) -> str:
    return f"call-{call_id.lower()}-{random.randint(1000, 9999)}"


async def dispatch_call(customer: dict, call_id: str | None = None) -> DispatchResult:
    """Create a LiveKit room and dispatch the outbound-caller agent into it.

    `customer` is passed through verbatim as job metadata (JSON-encoded), so
    any extra keys (call_id, request_id, callback_url, prompt_context) ride
    along and are visible to agent.py's entrypoint.

    Raises DispatchError on missing credentials or a LiveKit API failure.
    """
    if not (config.LIVEKIT_URL and config.LIVEKIT_API_KEY and config.LIVEKIT_API_SECRET):
        raise DispatchError(
            "Missing LiveKit credentials (LIVEKIT_URL/LIVEKIT_API_KEY/LIVEKIT_API_SECRET) in .env."
        )
    if not config.SIP_TRUNK_ID:
        raise DispatchError(
            "Missing VOBIZ_SIP_TRUNK_ID in .env. Run list_trunks.py / create_trunk.py."
        )

    call_id = call_id or customer.get("call_id") or f"CALL_{uuid.uuid4().hex[:10].upper()}"
    customer = {**customer, "call_id": call_id}
    room_name = _room_name_for(call_id)
    metadata = json.dumps(customer, ensure_ascii=False)

    lk_api = api.LiveKitAPI(
        url=config.LIVEKIT_URL,
        api_key=config.LIVEKIT_API_KEY,
        api_secret=config.LIVEKIT_API_SECRET,
    )
    try:
        dispatch_request = api.CreateAgentDispatchRequest(
            agent_name="outbound-caller",  # must match agent.py
            room=room_name,
            metadata=metadata,
        )
        dispatch = await lk_api.agent_dispatch.create_dispatch(dispatch_request)
        logger.info(
            "Dispatched outbound-caller -> room=%s call_id=%s phone=%s",
            room_name,
            call_id,
            customer.get("phone"),
        )
        return DispatchResult(dispatch_id=dispatch.id, room_name=room_name, call_id=call_id)
    except Exception as exc:
        raise DispatchError(str(exc)) from exc
    finally:
        await lk_api.aclose()
