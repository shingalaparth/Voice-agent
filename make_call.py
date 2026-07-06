"""Dispatch a Diorin outbound call for the customer in customer.json.

Flow: load + validate customer.json → create a unique LiveKit room → dispatch
the 'outbound-caller' agent with the full customer record in metadata.

Usage:
    python make_call.py
    python make_call.py --file path/to/other_customer.json
"""
from __future__ import annotations

import os

# SSL cert fix must run before any network imports on some platforms.
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import argparse
import asyncio
import json
import random
import sys

from dotenv import load_dotenv
from livekit import api

import config
from logger import logger
from storage import load_customer

load_dotenv(".env")


def _room_name_for(phone: str) -> str:
    return f"call-{phone.replace('+', '')}-{random.randint(1000, 9999)}"


async def dispatch(customer: dict) -> int:
    """Dispatch the agent to a fresh room. Returns a process exit code."""
    url = config.LIVEKIT_URL
    api_key = config.LIVEKIT_API_KEY
    api_secret = config.LIVEKIT_API_SECRET
    if not (url and api_key and api_secret):
        logger.error("Missing LiveKit credentials (LIVEKIT_URL/API_KEY/API_SECRET) in .env.")
        return 1

    trunk_id = config.SIP_TRUNK_ID
    if not trunk_id:
        logger.error("Missing VOBIZ_SIP_TRUNK_ID in .env. Run list_trunks.py / create_trunk.py.")
        return 1

    room_name = _room_name_for(customer["phone"])
    metadata = json.dumps(customer, ensure_ascii=False)
    phone = customer["phone"]

    logger.info(
        "Dispatching outbound-caller -> room=%s phone=%s order=%s",
        room_name,
        phone,
        customer["order_id"],
    )
    print(f"\n📞 Calling {customer['name']} at {phone}...")
    print(f"   Order : {customer['order_id']} — {customer['product']} ({customer['amount']})")
    print(f"   Room  : {room_name}")

    lk_api = api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret)
    try:
        dispatch_request = api.CreateAgentDispatchRequest(
            agent_name="outbound-caller",  # must match agent.py
            room=room_name,
            metadata=metadata,
        )
        dispatch = await lk_api.agent_dispatch.create_dispatch(dispatch_request)
        print("\n✅ Call dispatched successfully.")
        print(f"   Dispatch ID: {dispatch.id}")
        print("   Watch the agent terminal for the live conversation logs.")
        return 0
    except Exception as exc:
        logger.error("Failed to dispatch call: %s", exc, exc_info=True)
        print(f"\n❌ Error dispatching call: {exc}")
        return 1
    finally:
        await lk_api.aclose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a Diorin outbound call.")
    parser.add_argument(
        "--file",
        default=str(config.CUSTOMER_FILE),
        help="Path to a customer.json file (default: ./customer.json).",
    )
    args = parser.parse_args()

    try:
        customer = load_customer(args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌ {exc}")
        return 1

    return asyncio.run(dispatch(customer))


if __name__ == "__main__":
    sys.exit(main())
