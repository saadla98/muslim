"""تحميل بيانات الأذكار والأدعية من ملفّات JSON، مع فهرسة وبحث عربي مرِن."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache

from .config import DATA_DIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# تطبيع النص العربي للبحث (إزالة التشكيل وتوحيد الحروف)
# ---------------------------------------------------------------------------
_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْٰـ]")  # تشكيل + تطويل


def normalize(text: str) -> str:
    """توحيد النص العربي: إزالة التشكيل والتطويل وتوحيد الهمزات والتاء المربوطة."""
    if not text:
        return ""
    text = _DIACRITICS.sub("", text)
    text = (
        text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        .replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    )
    # إزالة علامات الترقيم والرموز مع إبقاء الحروف والأرقام والمسافات
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


# ---------------------------------------------------------------------------
# نماذج البيانات
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Entry:
    """ذكر أو دعاء واحد."""
    id: str
    category_id: str
    title: str
    text: str
    repeat: str = ""
    reference: str = ""
    benefit: str = ""
    keywords: tuple[str, ...] = field(default_factory=tuple)

    @property
    def uid(self) -> str:
        """معرّف فريد عبر كل التصنيفات (يُستعمل في أزرار البوت)."""
        return f"{self.category_id}:{self.id}"

    @property
    def search_blob(self) -> str:
        """النص المُطبَّع المستعمَل في المطابقة."""
        return normalize(" ".join([self.title, *self.keywords]))


@dataclass(frozen=True)
class Category:
    id: str
    title: str
    emoji: str
    command: str
    keywords: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# التحميل
# ---------------------------------------------------------------------------
def _read_json(name: str):
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load() -> tuple[list[Category], dict[str, list[Entry]]]:
    """تحميل التصنيفات وكل المداخل (مع التخزين المؤقّت)."""
    raw_categories = _read_json("categories.json")
    categories: list[Category] = []
    entries_by_cat: dict[str, list[Entry]] = {}

    for c in raw_categories:
        category = Category(
            id=c["id"],
            title=c["title"],
            emoji=c.get("emoji", "📿"),
            command=c.get("command", c["id"]),
            keywords=tuple(c.get("keywords", [])),
        )
        categories.append(category)

        items = _read_json(c["file"])
        entries_by_cat[category.id] = [
            Entry(
                id=item["id"],
                category_id=category.id,
                title=item["title"],
                text=item["text"],
                repeat=item.get("repeat", ""),
                reference=item.get("reference", ""),
                benefit=item.get("benefit", ""),
                keywords=tuple(item.get("keywords", [])),
            )
            for item in items
        ]

    total = sum(len(v) for v in entries_by_cat.values())
    logger.info("تم تحميل %d تصنيف و%d ذكر/دعاء.", len(categories), total)
    return categories, entries_by_cat


# ---------------------------------------------------------------------------
# واجهة الاستعلام
# ---------------------------------------------------------------------------
def get_categories() -> list[Category]:
    return _load()[0]


def get_category(category_id: str) -> Category | None:
    return next((c for c in get_categories() if c.id == category_id), None)


def get_entries(category_id: str) -> list[Entry]:
    return _load()[1].get(category_id, [])


def all_entries() -> list[Entry]:
    entries: list[Entry] = []
    for items in _load()[1].values():
        entries.extend(items)
    return entries


def get_entry(category_id: str, entry_id: str) -> Entry | None:
    return next((e for e in get_entries(category_id) if e.id == entry_id), None)


def find_category_by_query(query: str) -> Category | None:
    """مطابقة نصّ المستخدم مع اسم تصنيف (مثال: 'أذكار الصباح')."""
    q = normalize(query)
    if not q:
        return None
    for c in get_categories():
        blob = normalize(" ".join([c.title, *c.keywords]))
        if q == normalize(c.title) or q in blob or blob_contains_query(blob, q):
            return c
    return None


def blob_contains_query(blob: str, q: str) -> bool:
    """هل كل كلمات الاستعلام موجودة في النص؟"""
    words = q.split()
    return bool(words) and all(w in blob for w in words)


def search_scored(query: str, limit: int = 12) -> list[tuple[int, Entry]]:
    """بحث مرِن: يُرجِع أزواج (النقاط، المدخل) مرتّبة حسب قوّة المطابقة."""
    q = normalize(query)
    if not q:
        return []

    scored: list[tuple[int, Entry]] = []
    for e in all_entries():
        blob = e.search_blob
        norm_title = normalize(e.title)
        norm_keywords = [normalize(k) for k in e.keywords]

        score = 0
        if q == norm_title or q in norm_keywords:
            score = 100                       # مطابقة تامّة
        elif q in blob:
            score = 70                        # الاستعلام كسلسلة داخل النص
        elif blob_contains_query(blob, q):
            score = 50                        # كل كلمات الاستعلام موجودة
        else:
            # مطابقة جزئية: نسبة الكلمات الموجودة
            words = q.split()
            hits = sum(1 for w in words if w in blob)
            if hits:
                score = 20 + hits

        if score:
            if q in norm_title:               # ترجيح المطابقة في العنوان
                score += 10
            scored.append((score, e))

    scored.sort(key=lambda x: (-x[0], len(x[1].title)))

    # عند وجود مطابقة قويّة، احذف المطابقات الجزئية الضعيفة (تقليل الضجيج)
    if scored and scored[0][0] >= 70:
        scored = [pair for pair in scored if pair[0] >= 40]

    return scored[:limit]


def search(query: str, limit: int = 12) -> list[Entry]:
    """بحث مرِن: يُرجِع المداخل فقط مرتّبة حسب قوّة المطابقة."""
    return [e for _, e in search_scored(query, limit)]


def is_confident_match(scored: list[tuple[int, Entry]]) -> bool:
    """هل النتيجة الأولى إجابةٌ واضحة تُعرَض مباشرةً؟"""
    if not scored:
        return False
    top = scored[0][0]
    second = scored[1][0] if len(scored) > 1 else 0
    return top >= 100 or (top >= 60 and top - second >= 25)
