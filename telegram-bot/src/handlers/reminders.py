"""Handlers for the automatic-reminders menu (/tadkir) and its toggle buttons."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .. import config, storage
from ..keyboards import reminders_menu
from .callbacks import safe_answer

logger = logging.getLogger(__name__)

_KIND_LABEL = {"morning": "أذكار الصباح", "evening": "أذكار المساء"}


def _menu_text(prefs: dict[str, bool]) -> str:
    morning = "✅ مُفعّل" if prefs.get("morning") else "⬜ متوقّف"
    evening = "✅ مُفعّل" if prefs.get("evening") else "⬜ متوقّف"
    return (
        "⏰ <b>التذكير التلقائي</b>\n\n"
        "فعِّل التذكير ليصلَك في وقته بإذن الله، واضغط على الزرّ للتفعيل أو الإيقاف.\n\n"
        f"🌅 أذكار الصباح: <b>{morning}</b>\n"
        f"🌆 أذكار المساء: <b>{evening}</b>\n\n"
        f"🕐 المواعيد: الصباح <b>{config.MORNING_TIME}</b> — المساء <b>{config.EVENING_TIME}</b>\n"
        f"🌍 التوقيت: <i>{config.REMINDER_TIMEZONE}</i>"
    )


async def tadkir_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefs = storage.get_prefs(update.effective_chat.id)
    await update.effective_message.reply_html(
        _menu_text(prefs), reply_markup=reminders_menu(prefs)
    )


async def on_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data or ""
    chat_id = update.effective_chat.id

    # data format: rem:toggle:<kind>
    parts = data.split(":")
    if len(parts) == 3 and parts[1] == "toggle" and parts[2] in _KIND_LABEL:
        kind = parts[2]
        prefs = storage.get_prefs(chat_id)
        new_value = not prefs.get(kind)
        storage.set_pref(chat_id, kind, new_value)

        state = "تم تفعيل" if new_value else "تم إيقاف"
        await safe_answer(query, f"{state} تذكير {_KIND_LABEL[kind]}")

        prefs = storage.get_prefs(chat_id)
        await query.edit_message_text(
            _menu_text(prefs), parse_mode="HTML", reply_markup=reminders_menu(prefs)
        )
        return

    await safe_answer(query)
