"""Request/response models for the Voice AI API (main.py).

Kept separate from config.py / tools.py so the HTTP contract is easy to read
in one place and shows up cleanly in the auto-generated /docs.
"""
from __future__ import annotations

import re

from pydantic import BaseModel, Field, HttpUrl, field_validator

# Same E.164-ish check storage.py uses for customer.json, so a bad phone
# number is rejected at the HTTP boundary instead of failing deep inside a
# LiveKit dispatch call.
_PHONE_RE = re.compile(r"^\+?\d{8,15}$")


class CallRequest(BaseModel):
    request_id: str = Field(..., min_length=1, max_length=128)
    customer_name: str = Field(..., min_length=1, max_length=200)
    phone: str
    order_id: str = Field(..., min_length=1, max_length=100)
    product: str = Field(..., min_length=1, max_length=200)
    amount: str = Field(..., min_length=1, max_length=50)
    callback_url: HttpUrl
    # Optional extra context appended to the (otherwise fixed) Diorin COD
    # verification script -- NOT a full prompt replacement.
    prompt: str | None = Field(default=None, max_length=2000)
    language: str | None = Field(default=None, description="hi | en | multi")

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not _PHONE_RE.match(v):
            raise ValueError("phone must be E.164 format, e.g. +919876543210")
        return v


class CallAcceptedResponse(BaseModel):
    call_id: str
    status: str = "accepted"


class HealthResponse(BaseModel):
    status: str
    missing: list[str] = Field(default_factory=list)
