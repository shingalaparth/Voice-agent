"""Centralized logging for the communication platform.

Console + rotating file output under data/logs/. Import `logger` everywhere so
the whole project shares one configured logger.
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Resolve paths relative to this file so it works from any CWD.
# logger/ → communication/ → src/ → <repo root>. Runtime logs live in <repo>/data/logs/.
# NOTE: logger is the lowest layer — it must NOT import config (config imports logger).
# Both compute the same path via parents[3], so LOG_DIR stays in sync with config.LOG_DIR.
BASE_DIR = Path(__file__).resolve().parents[3]
LOG_DIR = BASE_DIR / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_logger() -> logging.Logger:
    """Configure and return the root project logger."""
    log = logging.getLogger("communication-agent")
    log.setLevel(logging.INFO)
    log.propagate = False  # avoid duplicate lines if root logger also emits

    if log.handlers:  # already configured (e.g. on reload)
        return log

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    log.addHandler(console)

    try:
        file_handler = RotatingFileHandler(
            LOG_DIR / "agent.log",
            maxBytes=2_000_000,  # ~2 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    except OSError as exc:
        # File logging is best-effort; never let it block startup.
        log.warning("File logging unavailable: %s", exc)

    return log


logger = _build_logger()
