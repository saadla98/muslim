"""نصوص الواجهة العربية وتنسيق الرسائل."""
from __future__ import annotations

from html import escape

from .data_loader import Category, Entry

BOT_NAME = "بوت الأذكار والأدعية"

WELCOME = (
    "🕌 <b>أهلًا بك في {name}</b>\n\n"
    "هنا تجد الأذكار والأدعية الصحيحة من السنّة النبوية بإذن الله.\n\n"
    "🔎 <b>كيف تستعمله؟</b>\n"
    "• اختر تصنيفًا من القائمة بالأسفل.\n"
    "• أو <b>اكتب اسم الدعاء مباشرةً</b> وسيجيبك البوت.\n"
    "   <i>مثال: اكتب «دعاء الخروج من المنزل»</i>\n\n"
    "اكتب /help لعرض كل الأوامر."
).format(name=BOT_NAME)

HELP = (
    "📖 <b>الأوامر المتاحة</b>\n\n"
    "/start — البداية والقائمة الرئيسية\n"
    "/menu — القائمة الرئيسية للتصنيفات\n"
    "/search — طريقة البحث\n"
    "/help — هذه المساعدة\n\n"
    "<b>أوامر التصنيفات:</b>\n"
    "{categories}\n\n"
    "🔎 <b>البحث بالكتابة:</b>\n"
    "اكتب اسم أي دعاء أو ذكر (بتشكيل أو بدونه) وسيبحث عنه البوت.\n"
    "<i>أمثلة: «أذكار الصباح» ، «دعاء السفر» ، «الكرب» ، «قبل النوم»</i>"
)

SEARCH_PROMPT = (
    "🔎 <b>البحث</b>\n\n"
    "اكتب اسم الذكر أو الدعاء الذي تريده وسأبحث عنه لك.\n"
    "<i>مثال: «دعاء الخروج من المنزل» أو «الهم والحزن»</i>"
)

MENU_TITLE = "📿 <b>اختر تصنيفًا:</b>"

NOT_FOUND = (
    "🤔 لم أجد نتيجة لـ «<b>{query}</b>».\n\n"
    "جرّب كلمات أخرى، أو اكتب /menu لتصفّح التصنيفات."
)

MULTIPLE_RESULTS = "🔎 وجدت <b>{count}</b> نتيجة لـ «<b>{query}</b>». اختر واحدة:"


def format_entry(entry: Entry, category: Category | None = None) -> str:
    """تنسيق ذكر/دعاء كرسالة HTML."""
    header = f"{category.emoji} " if category else "📿 "
    parts = [f"{header}<b>{escape(entry.title)}</b>", "", f"<code>{escape(entry.text)}</code>"]

    meta = []
    if entry.repeat:
        meta.append(f"🔁 <b>التكرار:</b> {escape(entry.repeat)}")
    if entry.benefit:
        meta.append(f"✨ <b>الفضل:</b> {escape(entry.benefit)}")
    if entry.reference:
        meta.append(f"📚 <b>المصدر:</b> <i>{escape(entry.reference)}</i>")
    if meta:
        parts.append("")
        parts.extend(meta)

    return "\n".join(parts)


def format_help() -> str:
    from .data_loader import get_categories

    lines = "\n".join(
        f"/{c.command} — {c.emoji} {c.title}" for c in get_categories()
    )
    return HELP.format(categories=lines)
