"""Diorin outbound voice agent.

LiveKit worker entrypoint. Receives the full customer record in job metadata
(from make_call.py), starts a Deepgram + Groq + ElevenLabs session, dials the
customer over the Vobiz SIP trunk, runs the COD verification conversation, and
guarantees the result is saved (via the shutdown callback even on hangup).
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

# SSL cert fix must run before any network imports on some platforms.
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

from livekit import agents, api
from livekit.agents import Agent, AgentSession, RoomInputOptions, llm
from livekit.plugins import deepgram, elevenlabs, openai

import config
from logger import logger
from prompts import build_greeting, build_system_prompt
from tools import OrderTools
import analysis_service



def _parse_customer(metadata_raw: str | None) -> dict | None:
    """Pull the customer record out of job/room metadata. Returns None if absent."""
    if not metadata_raw:
        return None
    try:
        data = json.loads(metadata_raw)
    except json.JSONDecodeError:
        logger.warning("Metadata was not valid JSON; ignoring.")
        return None
    if isinstance(data, dict) and data.get("name") and data.get("phone"):
        return data
    # Some payloads only carry phone_number (legacy make_call.py) — not enough for Diorin.
    return None


async def entrypoint(ctx: agents.JobContext) -> None:
    logger.info("Agent job started for room: %s", ctx.room.name)

    # --- 1. Resolve the customer record from metadata -------------------------
    customer = _parse_customer(getattr(ctx.job, "metadata", None)) or _parse_customer(
        getattr(ctx.room, "metadata", None)
    )
    if not customer:
        logger.error(
            "No customer record in job metadata. Dispatch via make_call.py so the "
            "agent receives name/phone/order_id/product/amount. Shutting down."
        )
        ctx.shutdown()
        return

    language = (customer.get("language") or config.DEFAULT_LANGUAGE).lower()
    logger.info(
        "Customer loaded: %s (%s) order=%s product=%s amount=%s lang=%s",
        customer.get("name"),
        customer.get("phone"),
        customer.get("order_id"),
        customer.get("product"),
        customer.get("amount"),
        language,
    )

    # --- 2. Build tools, session, and assistant -------------------------------
    order_tools = OrderTools(customer, ctx)

    # Guarantee the result is saved even if the customer hangs up mid-conversation
    # and the LLM never reaches save_call_result().
    async def _on_shutdown():
        try:
            out_path = order_tools.persist()
            if out_path and config.ENABLE_GEMINI_ANALYSIS:
                await analysis_service.analyze_call(Path(out_path))
        except Exception as exc:
            logger.error("Error in shutdown callback: %s", exc, exc_info=True)

    ctx.add_shutdown_callback(_on_shutdown)

    try:
        session = AgentSession(
            stt=deepgram.STT(model=config.STT_MODEL, language=language),
            llm=openai.LLM(
                base_url=config.GROQ_BASE_URL,
                api_key=config.GROQ_API_KEY,
                model=config.GROQ_MODEL,
                temperature=config.GROQ_TEMPERATURE,
            ),
            tts=elevenlabs.TTS(
                voice_id=config.ELEVENLABS_VOICE_ID,
                model=config.ELEVEN_MODEL,
            ),
        )

        instructions = build_system_prompt(customer, language)
        greeting = build_greeting(customer, language)

        agent_instance = Agent(
            instructions=instructions,
            tools=llm.find_function_tools(order_tools),
            min_endpointing_delay=0.5,
        )
        order_tools.agent = agent_instance

        await session.start(
            room=ctx.room,
            agent=agent_instance,
            room_input_options=RoomInputOptions(
                close_on_disconnect=True,
            ),
        )

        # --- 3. Dial the customer over SIP ---------------------------------------
        phone_number = customer["phone"]
        already_in_room = any(
            f"sip_{phone_number}" in p.identity for p in ctx.room.remote_participants.values()
        )

        if already_in_room:
            logger.info("Customer %s already in room; greeting directly.", phone_number)
            session.generate_reply(instructions=greeting)
            await asyncio.Event().wait()

        logger.info("Initiating outbound SIP call to %s via trunk %s", phone_number, config.SIP_TRUNK_ID)
        try:
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=config.SIP_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity=f"sip_{phone_number}",
                    wait_until_answered=True,
                )
            )
        except Exception as exc:
            logger.error("SIP call to %s failed: %s", phone_number, exc)
            order_tools.status = "FAILED"
            
            # Clean up the TwirpError string if possible to make the JSON logs readable
            exc_str = str(exc)
            if "486: Busy Here" in exc_str:
                order_tools.cancel_reason = "Customer is busy (SIP 486)"
            elif "480: Temporarily Unavailable" in exc_str:
                order_tools.cancel_reason = "Customer is unavailable (SIP 480)"
            else:
                order_tools.cancel_reason = f"SIP Error: {exc_str[:200]}"
                
            order_tools.persist()
            return

        masked_phone = f"{phone_number[:4]}****{phone_number[-4:]}" if len(phone_number) > 8 else "****"
        logger.info("Call answered by %s — agent is now speaking.", masked_phone)
        session.generate_reply(instructions=greeting)
        
        while ctx.room.isconnected():
            await asyncio.sleep(1)
            
            # If the tool saved the result, wait for the AI to finish speaking its goodbye
            if order_tools._saved:
                try:
                    await session.wait_for_idle()  # wait until TTS finishes the goodbye
                except Exception:
                    pass
                await asyncio.sleep(2)  # small buffer after audio ends
                logger.info("Explicitly kicking SIP customer before room disconnect.")
                try:
                    for p in list(ctx.room.remote_participants.values()):
                        if p.identity.startswith("sip_"):
                            await ctx.api.room.remove_participant(
                                api.RoomParticipantIdentity(
                                    room=ctx.room.name,
                                    identity=p.identity
                                )
                            )
                except Exception as exc:
                    logger.error("Failed to kick SIP participant: %s", exc)
                    
                logger.info("Auto-cutting call via room disconnect.")
                try:
                    await ctx.room.disconnect()
                except Exception:
                    pass
                await asyncio.sleep(0.5)  # flush buffer before context teardown to prevent Rust panics
                break
        
    except Exception as exc:
        logger.error("Unhandled error in call flow: %s", exc, exc_info=True)
        order_tools.status = "FAILED"
        order_tools.cancel_reason = f"Unhandled system error: {exc}"
        order_tools.persist()
    finally:
        try:
            if 'session' in locals():
                await session.aclose()
        except Exception:
            pass
        ctx.shutdown()


if __name__ == "__main__":
    # Validate credentials once before the worker accepts jobs.
    config.validate_env()
    logger.info("Starting Diorin outbound worker (agent_name=outbound-caller)...")
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller",
        )
    )
