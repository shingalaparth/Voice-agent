"""Centralized logging for the Diorin voice agent.

Console + rotating file output under logs/. Import `logger` everywhere so the
whole project shares one configured logger.
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Resolve paths relative to this file so it works from any CWD.
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_logger() -> logging.Logger:
    """Configure and return the root project logger."""
    log = logging.getLogger("diorin-agent")
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
