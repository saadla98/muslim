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
    """Category menu: a 'show all' button on top, then one button per entry."""
    rows = [
        [InlineKeyboardButton("📜 عرض الكل في رسالة واحدة", callback_data=f"all:{category.id}")]
    ]
    rows += [
        [InlineKeyboardButton(e.title, callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("⬅️ رجوع للقائمة", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def nav_buttons(category_id: str) -> InlineKeyboardMarkup:
    """Back-to-category and back-to-menu buttons."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ رجوع للتصنيف", callback_data=f"cat:{category_id}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")],
        ]
    )


def entry_nav(entry: Entry) -> InlineKeyboardMarkup:
    """Navigation buttons shown under a dhikr/du'a."""
    return nav_buttons(entry.category_id)


def results_menu(entries: list[Entry]) -> InlineKeyboardMarkup:
    """Search results as buttons."""
    rows = [
        [InlineKeyboardButton(f"{e.title}", callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def open_category(category_id: str, label: str) -> InlineKeyboardMarkup:
    """A single button that opens a category (used in reminder messages)."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"cat:{category_id}")]]
    )


def reminders_menu(prefs: dict[str, bool]) -> InlineKeyboardMarkup:
    """Toggle buttons for the automatic morning/evening reminders."""
    morning = "✅" if prefs.get("morning") else "⬜"
    evening = "✅" if prefs.get("evening") else "⬜"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"{morning} 🌅 تذكير أذكار الصباح", callback_data="rem:toggle:morning")],
            [InlineKeyboardButton(f"{evening} 🌆 تذكير أذكار المساء", callback_data="rem:toggle:evening")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")],
        ]
    )
