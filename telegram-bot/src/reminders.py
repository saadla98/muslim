"""Automatic daily reminders for the morning/evening adhkar.

Uses python-telegram-bot's JobQueue (APScheduler) to fire two daily jobs at
the times configured in .env, each sending a message to the subscribers of
that reminder kind.
"""
from __future__ import annotations

import datetime
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import Application, ContextTypes

from . import config, storage
from .keyboards import open_category

logger = logging.getLogger(__name__)

# kind -> (category_id, button label, message)
_REMINDERS = {
    "morning": (
        "sabah",
        "🌅 افتح أذكار الصباح",
        "🌅 <b>تذكير: أذكار الصباح</b>\n\n"
        "لا تنسَ أذكارَ الصباح، فهي حِصنُك وحِرزُك بإذن الله. 🤲",
    ),
    "evening": (
        "masaa",
        "🌆 افتح أذكار المساء",
        "🌆 <b>تذكير: أذكار المساء</b>\n\n"
        "حان وقتُ أذكار المساء، فحصِّن نفسَك بذكر الله. 🤲",
    ),
}


def _timezone() -> ZoneInfo:
    try:
        return ZoneInfo(config.REMINDER_TIMEZONE)
    except (ZoneInfoNotFoundError, ValueError):
        logger.warning("Unknown timezone %r, using UTC.", config.REMINDER_TIMEZONE)
        return ZoneInfo("UTC")


async def _send_reminder(context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    category_id, label, message = _REMINDERS[kind]
    chat_ids = storage.subscribers(kind)
    logger.info("Sending %s reminder to %d subscriber(s).", kind, len(chat_ids))

    markup = open_category(category_id, label)
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
        except Forbidden:
            # User blocked or deleted the bot -> stop bothering them.
            logger.info("Chat %s blocked the bot; removing from subscribers.", chat_id)
            storage.remove(chat_id)
        except TelegramError as exc:
            logger.warning("Failed to send %s reminder to %s: %s", kind, chat_id, exc)


async def _morning_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_reminder(context, "morning")


async def _evening_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_reminder(context, "evening")


def schedule(app: Application) -> None:
    """Register the two daily reminder jobs. Safe to call once at startup."""
    if app.job_queue is None:
        logger.error(
            "JobQueue is unavailable; install 'python-telegram-bot[job-queue]'. "
            "Reminders are disabled."
        )
        return

    tz = _timezone()
    morning = config.parse_time(config.MORNING_TIME, default=(6, 30))
    evening = config.parse_time(config.EVENING_TIME, default=(17, 30))

    app.job_queue.run_daily(
        _morning_job,
        time=datetime.time(morning.hour, morning.minute, tzinfo=tz),
        name="morning_reminder",
    )
    app.job_queue.run_daily(
        _evening_job,
        time=datetime.time(evening.hour, evening.minute, tzinfo=tz),
        name="evening_reminder",
    )
    logger.info(
        "Scheduled reminders — morning %02d:%02d, evening %02d:%02d (%s).",
        morning.hour, morning.minute, evening.hour, evening.minute, config.REMINDER_TIMEZONE,
    )
