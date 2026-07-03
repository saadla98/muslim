"""لوحات الأزرار (Inline Keyboards) الخاصّة بالبوت.

مخطّط بيانات الأزرار (callback_data):
    menu                 → القائمة الرئيسية
    help                 → المساعدة
    cat:<category_id>    → عرض مداخل تصنيف
    ent:<category_id>:<entry_id>  → عرض ذكر/دعاء
"""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .data_loader import Category, Entry, get_categories


def main_menu() -> InlineKeyboardMarkup:
    """القائمة الرئيسية: زرّان في كل صفّ للتصنيفات."""
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
    """قائمة مداخل تصنيف: زرّ لكل ذكر/دعاء، ثم زرّ الرجوع."""
    rows = [
        [InlineKeyboardButton(e.title, callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("⬅️ رجوع للقائمة", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def entry_nav(entry: Entry) -> InlineKeyboardMarkup:
    """أزرار التنقّل أسفل ذكر/دعاء."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ رجوع للتصنيف", callback_data=f"cat:{entry.category_id}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")],
        ]
    )


def results_menu(entries: list[Entry]) -> InlineKeyboardMarkup:
    """قائمة نتائج البحث كأزرار."""
    rows = [
        [InlineKeyboardButton(f"{e.title}", callback_data=f"ent:{e.category_id}:{e.id}")]
        for e in entries
    ]
    rows.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(rows)
