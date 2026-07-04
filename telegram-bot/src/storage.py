"""Tiny JSON-backed store for reminder subscribers.

Shape on disk (subscribers.json):
    { "<chat_id>": { "morning": true, "evening": false }, ... }

The bot runs a single async event loop, so a plain dict + save-on-change is
enough; there is no cross-process concurrency to guard against.
"""
from __future__ import annotations

import json
import logging

from .config import SUBSCRIBERS_FILE

logger = logging.getLogger(__name__)

# chat_id (str) -> {"morning": bool, "evening": bool}
_subs: dict[str, dict[str, bool]] = {}
_loaded = False


def load() -> None:
    """Load subscribers from disk into memory (once)."""
    global _loaded
    _subs.clear()
    if SUBSCRIBERS_FILE.exists():
        try:
            with SUBSCRIBERS_FILE.open(encoding="utf-8") as f:
                raw = json.load(f)
            for chat_id, prefs in raw.items():
                _subs[str(chat_id)] = {
                    "morning": bool(prefs.get("morning", False)),
                    "evening": bool(prefs.get("evening", False)),
                }
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read subscribers file: %s", exc)
    _loaded = True
    logger.info("Loaded %d reminder subscriber(s).", len(_subs))


def _save() -> None:
    try:
        with SUBSCRIBERS_FILE.open("w", encoding="utf-8") as f:
            json.dump(_subs, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.error("Could not write subscribers file: %s", exc)


def get_prefs(chat_id: int) -> dict[str, bool]:
    """Return {'morning': bool, 'evening': bool} for a chat (defaults to off)."""
    return _subs.get(str(chat_id), {"morning": False, "evening": False}).copy()


def set_pref(chat_id: int, kind: str, value: bool) -> None:
    """Enable/disable one reminder kind ('morning' or 'evening') for a chat."""
    key = str(chat_id)
    entry = _subs.setdefault(key, {"morning": False, "evening": False})
    entry[kind] = value
    # Drop the record entirely if the user disabled everything.
    if not entry["morning"] and not entry["evening"]:
        _subs.pop(key, None)
    _save()


def remove(chat_id: int) -> None:
    """Remove a chat completely (e.g. the user blocked the bot)."""
    if _subs.pop(str(chat_id), None) is not None:
        _save()


def subscribers(kind: str) -> list[int]:
    """Chat ids subscribed to a given reminder kind."""
    return [int(cid) for cid, prefs in _subs.items() if prefs.get(kind)]
