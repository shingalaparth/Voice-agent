"""Configuration for the Diorin voice agent.

Holds environment variables, model settings, and resolved paths ONLY.
Prompts live in prompts.py. Business tools live in tools.py.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from logger import logger

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# =========================================================================================
# Paths
# =========================================================================================
CUSTOMER_FILE = BASE_DIR / "customer.json"
RESULTS_DIR = BASE_DIR / "call_results"
LOG_DIR = BASE_DIR / "logs"


# =========================================================================================
# Speech-to-Text (Deepgram)
# =========================================================================================
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
# nova-3 transcribes Hindi and Hindi-English mixed speech better than nova-2.
STT_MODEL = os.getenv("STT_MODEL", "nova-3")
# Default Hindi; override per-call via customer.json "language" or globally here.
# Use "multi" for Deepgram's auto-language detection once you scale beyond hi/en.
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "hi")


# =========================================================================================
# Text-to-Speech (ElevenLabs)
# =========================================================================================
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY") or os.getenv("ELEVENLABS_API_KEY") or ""
# eleven_turbo_v2_5 is multilingual and handles Hindi/English well.
ELEVEN_MODEL = os.getenv("ELEVEN_MODEL", "eleven_turbo_v2_5")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "tA6LGZpsqStKtSaGiXND")


# =========================================================================================
# Large Language Model (Groq via OpenAI-compatible client)
# =========================================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


# =========================================================================================
# Analysis (Gemini)
# =========================================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ANALYSIS_PROMPT_VERSION = "v1"


# =========================================================================================
# LiveKit
# =========================================================================================
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")


# =========================================================================================
# Telephony / SIP (Vobiz)
# =========================================================================================
SIP_TRUNK_ID = os.getenv("VOBIZ_SIP_TRUNK_ID") or os.getenv("OUTBOUND_TRUNK_ID", "")
SIP_DOMAIN = os.getenv("VOBIZ_SIP_DOMAIN", "")


# =========================================================================================
# Conversation
# =========================================================================================
# Default language when customer.json omits "language". hi | en | multi
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "hi")


# =========================================================================================
# Silence / No-Response Handling
# =========================================================================================
SILENCE_REPROMPT_DELAY = float(os.getenv("SILENCE_REPROMPT_DELAY", "4.0"))   # seconds before re-prompt
SILENCE_MAX_REPROMPTS = int(os.getenv("SILENCE_MAX_REPROMPTS", "2"))          # re-prompt N times before giving up
# No silence logic runs during this window right after the greeting: STT is
# warming up and the customer is usually still saying "Hello?". Prevents false
# re-prompts that talk over the customer's first response.
SILENCE_STARTUP_GRACE = float(os.getenv("SILENCE_STARTUP_GRACE", "5.0"))


# =========================================================================================
# Feature Flags
# =========================================================================================
# Set to "false" to disable saving conversation transcripts in the JSON result.
ENABLE_TRANSCRIPTION = os.getenv("ENABLE_TRANSCRIPTION", "true").lower() == "true"
# Set to "false" to disable Gemini post-call analysis.
ENABLE_GEMINI_ANALYSIS = os.getenv("ENABLE_GEMINI_ANALYSIS", "true").lower() == "true"


def validate_env() -> None:
    """Fail fast at startup if a required credential is missing.

    Logs each missing variable so the operator can fix .env in one pass.
    """
    required = {
        "LIVEKIT_URL": LIVEKIT_URL,
        "LIVEKIT_API_KEY": LIVEKIT_API_KEY,
        "LIVEKIT_API_SECRET": LIVEKIT_API_SECRET,
        "DEEPGRAM_API_KEY": DEEPGRAM_API_KEY,
        "GROQ_API_KEY": GROQ_API_KEY,
        "ELEVEN_API_KEY": ELEVEN_API_KEY,
        "VOBIZ_SIP_TRUNK_ID": SIP_TRUNK_ID,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        msg = (
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Check .env (see README for the full list)."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(
        "Env OK. STT=%s/%s TTS=elevenlabs/%s LLM=groq/%s Trunk=%s",
        STT_MODEL,
        STT_LANGUAGE,
        ELEVEN_MODEL,
        GROQ_MODEL,
        SIP_TRUNK_ID,
    )
