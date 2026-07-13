"""Voice AI API -- stateless HTTP entrypoint for the Diorin outbound agent.

Accepts a call request, dispatches the existing LiveKit agent (agent.py,
run separately via `python agent.py start`), and returns immediately. The
agent worker delivers the result to the caller's callback_url via a signed
webhook (see webhook.py) once the call finishes -- this process never waits
on a call and never returns call results directly.

Run with: uvicorn communication.api.main:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import os

# SSL cert fix must run before any network imports on some platforms.
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from communication.config import config
from communication.identity.auth import verify_api_key
from communication.providers.telephony.livekit.dispatch import DispatchError, dispatch_call
from communication.logging.logger import logger
from communication.api.schemas import CallAcceptedResponse, CallRequest, HealthResponse

app = FastAPI(
    title="Voice AI API",
    description=(
        "Stateless outbound voice-call platform. Submit a call, get an "
        "immediate acknowledgement, and receive the transcript + outcome "
        "via a signed webhook once the call completes."
    ),
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> JSONResponse:
    """Cheap liveness/readiness check -- confirms required credentials are
    configured. Does not ping LiveKit/Deepgram/Groq/ElevenLabs directly."""
    missing = config.missing_required_env()
    if missing:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "missing": missing},
        )
    return JSONResponse(status_code=200, content={"status": "ok", "missing": []})


@app.post(
    "/v1/calls",
    response_model=CallAcceptedResponse,
    status_code=202,
    dependencies=[Depends(verify_api_key)],
    tags=["calls"],
)
async def create_call(payload: CallRequest) -> CallAcceptedResponse:
    """Start a new AI voice call. Returns immediately with a call_id; the
    result is delivered later to `callback_url` as a signed webhook."""
    call_id = f"CALL_{uuid.uuid4().hex[:10].upper()}"

    customer = {
        "name": payload.customer_name,
        "phone": payload.phone,
        "order_id": payload.order_id,
        "product": payload.product,
        "amount": payload.amount,
        "language": payload.language or config.DEFAULT_LANGUAGE,
        "call_id": call_id,
        "request_id": payload.request_id,
        "callback_url": str(payload.callback_url),
        "prompt_context": payload.prompt,
    }

    try:
        result = await dispatch_call(customer, call_id=call_id)
    except DispatchError as exc:
        logger.error("Dispatch failed for request_id=%s: %s", payload.request_id, exc)
        raise HTTPException(status_code=502, detail=f"Failed to start call: {exc}") from exc
    except Exception as exc:  # never leak a raw stack trace to the client
        logger.error("Unexpected dispatch error for request_id=%s: %s", payload.request_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error while starting the call.") from exc

    return CallAcceptedResponse(call_id=result.call_id, status="accepted")
