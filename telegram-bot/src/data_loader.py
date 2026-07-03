"""Load adhkar & du'a data from JSON files, with indexing and flexible Arabic search."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache

from .config import DATA_DIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Arabic text normalization for search (strip diacritics, unify letters)
# ---------------------------------------------------------------------------
# The character class is built from explicit codepoint ranges (not literal
# diacritics) so it can only ever cover combining marks / tatweel, never the
# Arabic base letters (U+0621-U+064A) or the Arabic-Indic digits (U+0660-U+0669).
_DIACRITIC_RANGES = (
    (0x0610, 0x061A),  # honorific / Quranic signs
    (0x0640, 0x0640),  # tatweel (kashida)
    (0x064B, 0x065F),  # harakat and combining marks
    (0x0670, 0x0670),  # superscript alef
    (0x06D6, 0x06ED),  # Quranic annotation marks
)
_DIACRITICS = re.compile(
    "[" + "".join(f"{chr(lo)}-{chr(hi)}" for lo, hi in _DIACRITIC_RANGES) + "]"
)

# Letter-unification map applied after diacritics are stripped.
# Keys/values are common base letters, which round-trip reliably.
_UNIFY_TABLE = str.maketrans(
    {
        "أ": "ا",  # ALEF WITH HAMZA ABOVE -> ALEF
        "إ": "ا",  # ALEF WITH HAMZA BELOW -> ALEF
        "آ": "ا",  # ALEF WITH MADDA       -> ALEF
        "ى": "ي",  # ALEF MAKSURA          -> YEH
        "ة": "ه",  # TEH MARBUTA           -> HEH
        "ؤ": "و",  # WAW WITH HAMZA        -> WAW
        "ئ": "ي",  # YEH WITH HAMZA        -> YEH
    }
)


def normalize(text: str) -> str:
    """Normalize Arabic text: strip diacritics/tatweel, unify hamza and ta-marbuta."""
    if not text:
        return ""
    text = _DIACRITICS.sub("", text)
    text = text.translate(_UNIFY_TABLE)
    # Drop punctuation/symbols, keep letters, digits and spaces
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Entry:
    """A single dhikr or du'a."""
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
        """Unique id across all categories (used in bot buttons)."""
        return f"{self.category_id}:{self.id}"

    @property
    def search_blob(self) -> str:
        """Normalized text used for matching."""
        return normalize(" ".join([self.title, *self.keywords]))


@dataclass(frozen=True)
class Category:
    id: str
    title: str
    emoji: str
    command: str
    keywords: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _read_json(name: str):
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load() -> tuple[list[Category], dict[str, list[Entry]]]:
    """Load categories and all entries (cached)."""
    raw_categories = _read_json("categories.json")
    categories: list[Category] = []
    entries_by_cat: dict[str, list[Entry]] = {}

    for c in raw_categories:
        category = Category(
            id=c["id"],
            title=c["title"],
            emoji=c.get("emoji", "\U0001F4FF"),
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
    logger.info("Loaded %d categories and %d adhkar/du'as.", len(categories), total)
    return categories, entries_by_cat


# ---------------------------------------------------------------------------
# Query API
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
    """Match user text against a category title (e.g. the morning-adhkar name)."""
    q = normalize(query)
    if not q:
        return None
    for c in get_categories():
        blob = normalize(" ".join([c.title, *c.keywords]))
        if q == normalize(c.title) or q in blob or blob_contains_query(blob, q):
            return c
    return None


def blob_contains_query(blob: str, q: str) -> bool:
    """Are all query words present in the blob?"""
    words = q.split()
    return bool(words) and all(w in blob for w in words)


def search_scored(query: str, limit: int = 12) -> list[tuple[int, Entry]]:
    """Flexible search: return (score, entry) pairs sorted by match strength."""
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
            score = 100                       # exact match
        elif q in blob:
            score = 70                        # query as a substring of the blob
        elif blob_contains_query(blob, q):
            score = 50                        # all query words present
        else:
            # partial match: how many query words are present
            words = q.split()
            hits = sum(1 for w in words if w in blob)
            if hits:
                score = 20 + hits

        if score:
            if q in norm_title:               # boost matches in the title
                score += 10
            scored.append((score, e))

    scored.sort(key=lambda x: (-x[0], len(x[1].title)))

    # With a strong match present, drop weak partial matches to cut noise
    if scored and scored[0][0] >= 70:
        scored = [pair for pair in scored if pair[0] >= 40]

    return scored[:limit]


def search(query: str, limit: int = 12) -> list[Entry]:
    """Flexible search: return only the entries sorted by match strength."""
    return [e for _, e in search_scored(query, limit)]


def is_confident_match(scored: list[tuple[int, Entry]]) -> bool:
    """Is the top result a clear answer we can show directly?"""
    if not scored:
        return False
    top = scored[0][0]
    second = scored[1][0] if len(scored) > 1 else 0
    return top >= 100 or (top >= 60 and top - second >= 25)
