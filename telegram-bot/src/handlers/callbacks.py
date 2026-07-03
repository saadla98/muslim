"""معالج ضغطات الأزرار (CallbackQuery)."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .. import texts
from ..data_loader import get_category, get_entries, get_entry
from ..keyboards import category_menu, entry_nav, main_menu

logger = logging.getLogger(__name__)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # إزالة مؤشّر التحميل
    data = query.data or ""

    if data == "menu":
        await query.edit_message_text(
            texts.MENU_TITLE, parse_mode="HTML", reply_markup=main_menu()
        )
        return

    if data == "help":
        await query.edit_message_text(texts.format_help(), parse_mode="HTML")
        return

    if data.startswith("cat:"):
        category_id = data[len("cat:") :]
        category = get_category(category_id)
        if not category:
            await query.edit_message_text("⚠️ تصنيف غير موجود.")
            return
        entries = get_entries(category_id)
        title = f"{category.emoji} <b>{category.title}</b>\n\nاختر الذكر أو الدعاء:"
        await query.edit_message_text(
            title, parse_mode="HTML", reply_markup=category_menu(category, entries)
        )
        return

    if data.startswith("ent:"):
        try:
            _, category_id, entry_id = data.split(":", 2)
        except ValueError:
            await query.edit_message_text("⚠️ طلب غير صالح.")
            return
        entry = get_entry(category_id, entry_id)
        if not entry:
            await query.edit_message_text("⚠️ لم يُعثَر على هذا الذكر.")
            return
        category = get_category(category_id)
        await query.edit_message_text(
            texts.format_entry(entry, category),
            parse_mode="HTML",
            reply_markup=entry_nav(entry),
        )
        return

    logger.warning("callback_data غير معروف: %s", data)
