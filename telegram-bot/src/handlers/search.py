"""البحث بالكتابة: يكتب المستخدم اسم دعاء/ذكر فيجيبه البوت."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import texts
from ..data_loader import (
    find_category_by_query,
    get_category,
    get_entries,
    is_confident_match,
    search_scored,
)
from ..keyboards import category_menu, entry_nav, results_menu


async def do_search(update: Update, query: str) -> None:
    """المنطق الأساسي للبحث (يُستعمَل من النصّ ومن /search)."""
    message = update.effective_message
    query = query.strip()

    # 1) هل يطابق النصُّ اسمَ تصنيف كامل؟ (مثال: «أذكار الصباح»)
    category = find_category_by_query(query)
    if category:
        entries = get_entries(category.id)
        title = f"{category.emoji} <b>{category.title}</b>\n\nاختر الذكر أو الدعاء:"
        await message.reply_html(title, reply_markup=category_menu(category, entries))
        return

    # 2) بحث في المداخل
    scored = search_scored(query)

    if not scored:
        await message.reply_html(texts.NOT_FOUND.format(query=query))
        return

    results = [e for _, e in scored]

    # نتيجة واحدة أو مطابقة واثقة → اعرض الدعاء مباشرةً
    if len(results) == 1 or is_confident_match(scored):
        entry = results[0]
        cat = get_category(entry.category_id)
        await message.reply_html(
            texts.format_entry(entry, cat), reply_markup=entry_nav(entry)
        )
        return

    # نتائج متعدّدة → اعرضها كأزرار
    await message.reply_html(
        texts.MULTIPLE_RESULTS.format(count=len(results), query=query),
        reply_markup=results_menu(results),
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.effective_message.text or "").strip()
    if not text:
        return
    await do_search(update, text)
