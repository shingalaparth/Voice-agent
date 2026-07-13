"""API key authentication for the Voice AI API.

Every request to a protected endpoint must include:
    Authorization: Bearer <API_KEY>
"""
from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from communication.config import config


async def verify_api_key(authorization: str | None = Header(default=None)) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected 'Bearer <API_KEY>'.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or not hmac.compare_digest(token, config.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
