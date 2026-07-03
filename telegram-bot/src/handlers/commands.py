"""معالجات الأوامر: /start /help /menu /search + أوامر التصنيفات."""
from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import texts
from ..data_loader import Category, get_category, get_entries
from ..keyboards import category_menu, main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(
        texts.WELCOME, reply_markup=main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(texts.format_help())


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(
        texts.MENU_TITLE, reply_markup=main_menu()
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # إن كتب المستخدم: /search كلمة  → ابحث مباشرةً
    query = " ".join(context.args) if context.args else ""
    if query.strip():
        from .search import do_search

        await do_search(update, query)
    else:
        await update.effective_message.reply_html(texts.SEARCH_PROMPT)


async def _send_category(update: Update, category: Category) -> None:
    entries = get_entries(category.id)
    title = f"{category.emoji} <b>{category.title}</b>\n\nاختر الذكر أو الدعاء:"
    await update.effective_message.reply_html(
        title, reply_markup=category_menu(category, entries)
    )


def make_category_command(category_id: str):
    """ينشئ معالج أمر مربوطًا بتصنيف معيّن (مثال: /sabah)."""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        category = get_category(category_id)
        if category:
            await _send_category(update, category)

    return handler
