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
import sys

from dotenv import load_dotenv

from communication.config import config
from communication.providers.telephony.livekit.dispatch import DispatchError, dispatch_call
from communication.logging.logger import logger
from communication.persistence.storage import load_customer

load_dotenv(".env")


async def dispatch(customer: dict) -> int:
    """Dispatch the agent to a fresh room. Returns a process exit code."""
    phone = customer["phone"]
    print(f"\n📞 Calling {customer['name']} at {phone}...")
    print(f"   Order : {customer['order_id']} — {customer['product']} ({customer['amount']})")

    try:
        result = await dispatch_call(customer)
        print(f"   Room  : {result.room_name}")
        print("\n✅ Call dispatched successfully.")
        print(f"   Dispatch ID: {result.dispatch_id}")
        print(f"   Call ID    : {result.call_id}")
        print("   Watch the agent terminal for the live conversation logs.")
        return 0
    except DispatchError as exc:
        logger.error("Failed to dispatch call: %s", exc, exc_info=True)
        print(f"\n❌ Error dispatching call: {exc}")
        return 1


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
