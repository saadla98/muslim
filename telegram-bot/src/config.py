"""إعدادات البوت: قراءة المتغيّرات من البيئة (.env)."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# جذر مجلّد البوت (telegram-bot/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# تحميل متغيّرات البيئة من .env إن وُجد
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()


def configure_logging() -> None:
    """تهيئة نظام السجلّات."""
    # فرض ترميز UTF-8 على المخرجات حتى تظهر العربية في طرفيّة ويندوز (cp1252)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )
    # تقليل ضجيج مكتبة الشبكة
    logging.getLogger("httpx").setLevel(logging.WARNING)


def validate() -> None:
    """التأكّد من وجود التوكن قبل التشغيل."""
    if not BOT_TOKEN:
        raise SystemExit(
            "\n❌ لم يتم ضبط BOT_TOKEN.\n"
            "   انسخ .env.example إلى .env وضع توكن البوت من @BotFather.\n"
        )
