"""Local JSON storage for the Diorin MVP.

Two responsibilities:
  * load_customer()  - read the manually-edited customer.json (the call input).
  * save_result()    - write the final call outcome to call_results/*.json.

No database, ORM, or SQL. Pure filesystem JSON for the MVP.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logger import logger

BASE_DIR = Path(__file__).resolve().parent
CUSTOMER_FILE = BASE_DIR / "customer.json"
RESULTS_DIR = BASE_DIR / "call_results"

# Required keys for a customer record. Optional keys are ignored during validation.
REQUIRED_FIELDS = ("name", "phone", "order_id", "product", "amount")

# E.164-ish: optional leading +, then 8-15 digits. Good enough for MVP dialing.
_PHONE_RE = re.compile(r"^\+?\d{8,15}$")


def load_customer(path: Path | str = CUSTOMER_FILE) -> dict[str, Any]:
    """Load and validate the customer record from customer.json.

    Raises FileNotFoundError if missing, ValueError if invalid. The caller
    (make_call.py) turns these into clear user-facing messages.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"customer.json not found at {path}. Copy customer.example.json "
            "to customer.json and fill in the customer's details."
        )

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"customer.json is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("customer.json must contain a JSON object.")

    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        raise ValueError(
            f"customer.json is missing required field(s): {', '.join(missing)}"
        )

    phone = str(data["phone"]).strip()
    if not _PHONE_RE.match(phone):
        raise ValueError(
            f"Invalid phone number '{phone}'. Use E.164 format, e.g. +919876543210."
        )

    # Normalize: ensure language has a default; leave other optional fields alone.
    data.setdefault("language", "hi")
    logger.info("Customer loaded: %s (%s) — order %s", data["name"], phone, data["order_id"])
    return data


def _sanitize(text: str) -> str:
    """Make a string safe to embed in a filename."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_") or "unknown"


def save_result(result: dict[str, Any]) -> Path:
    """Write a call result dict to call_results/<timestamp>_<order_id>.json.

    Fills call_end_time and call_duration if missing. Returns the file path.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    start_iso = result.get("call_start_time")
    end_iso = result.get("call_end_time")
    if start_iso and not end_iso:
        end_iso = datetime.now(timezone.utc).isoformat()
        result["call_end_time"] = end_iso

    if start_iso and end_iso:
        try:
            start = datetime.fromisoformat(start_iso)
            end = datetime.fromisoformat(end_iso)
            result.setdefault("call_duration_seconds", round((end - start).total_seconds(), 1))
        except ValueError:
            logger.warning("Could not compute call duration from provided timestamps.")
            start = datetime.now(timezone.utc)
    else:
        # Fallback if timestamps are missing
        start = start_iso and datetime.fromisoformat(start_iso) or datetime.now(timezone.utc)

    # Use the call_start_time (or current time if missing) to ensure stable filenames for periodic saves.
    timestamp = start.strftime("%Y%m%d_%H%M%S")
    order_id = _sanitize(str(result.get("order_id", "noorder")))
    out_path = RESULTS_DIR / f"{timestamp}_{order_id}.json"

    try:
        tmp_path = out_path.with_suffix('.tmp')
        tmp_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(tmp_path, out_path)
        logger.info("Result saved to %s", out_path)
    except OSError as exc:
        logger.error("Failed to write result file %s: %s", out_path, exc)
        try:
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise

    return out_path
