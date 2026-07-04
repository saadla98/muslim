"""Bot configuration: read settings from the environment (.env)."""
from __future__ import annotations

import datetime
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Root of the bot folder (telegram-bot/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Runtime file holding the reminder subscribers (not tracked in git)
SUBSCRIBERS_FILE = BASE_DIR / "subscribers.json"

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()

# ----- Automatic reminders (morning / evening adhkar) -----
REMINDER_TIMEZONE: str = os.getenv("REMINDER_TIMEZONE", "Africa/Casablanca").strip()
MORNING_TIME: str = os.getenv("MORNING_TIME", "06:30").strip()
EVENING_TIME: str = os.getenv("EVENING_TIME", "17:30").strip()


def parse_time(value: str, default: tuple[int, int] = (6, 30)) -> datetime.time:
    """Parse a 'HH:MM' string into a naive datetime.time (falls back to default)."""
    try:
        hour, minute = (int(p) for p in value.strip().split(":", 1))
        return datetime.time(hour=hour, minute=minute)
    except (ValueError, AttributeError):
        return datetime.time(hour=default[0], minute=default[1])


def configure_logging() -> None:
    """Set up the logging system."""
    # Force UTF-8 on the output streams so Arabic shows correctly
    # in the Windows console (cp1252).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )
    # Reduce noise from the network library
    logging.getLogger("httpx").setLevel(logging.WARNING)


def validate() -> None:
    """Make sure the token is set before starting."""
    if not BOT_TOKEN:
        raise SystemExit(
            "\n❌ BOT_TOKEN is not set.\n"
            "   Copy .env.example to .env and put your bot token from @BotFather.\n"
        )
