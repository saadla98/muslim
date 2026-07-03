"""Inline keyboards used by the bot.

callback_data scheme:
    menu                          -> main menu
    help                          -> help
    cat:<category_id>             -> show a category's entries
    ent:<category_id>:<entry_id>  -> show a dhikr/du'a
"""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .data_loader import Category, Entry, get_categories


def main_menu() -> InlineKeyboardMarkup:
    """Main menu: two category buttons per row."""
    cats = get_categories()
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(cats), 2):
        row = [
            InlineKeyboardButton(f"{c.emoji} {c.title}", callback_data=f"cat:{c.id}")
            for c in cats[i : i + 2]
        ]
        rows.append(row)
    rows.append([InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")])
    return InlineKeyboardMarkup(rows)


def category_menu(category: Category, entries: list[Entry]) -> InlineKeyboardMarkup:
    """Category menu: one button per entry, then a back button."""
    rows = [
        [InlineKeyboardButton(e.title, callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("⬅️ رجوع للقائمة", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def entry_nav(entry: Entry) -> InlineKeyboardMarkup:
    """Navigation buttons shown under a dhikr/du'a."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ رجوع للتصنيف", callback_data=f"cat:{entry.category_id}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")],
        ]
    )


def results_menu(entries: list[Entry]) -> InlineKeyboardMarkup:
    """Search results as buttons."""
    rows = [
        [InlineKeyboardButton(f"{e.title}", callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(rows)
