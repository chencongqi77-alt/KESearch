"""Conservative comparisons for bibliographies with spacing and OCR artifacts."""
from __future__ import annotations

import re
import unicodedata


def _fold(text):
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_title(text):
    """Word tokens for queries and author matching."""
    return " ".join(re.findall(r"[^\W_]+", _fold(text)))


def title_identity_key(title):
    """Full title for identity checks. Preserve meaningful punctuation such as C++ and C#."""
    title = _fold(title).strip().rstrip(".")
    title = re.sub(r"(?<=[^\W\d_])-\s*\\?[\x60´]\s*(?=[^\W\d_])", "", title)
    return re.sub(r"[\s\u00ad\-‐‑‒–—]+", "", title)


def cited_metadata(ref):
    title, entry = ref.get("title"), ref.get("entry")
    if not title or not entry or title == entry or len(title) > 500:
        return None
    before, sep, venue = entry.partition(title)
    if not sep:
        return None
    # Allow for author-year styles which put the year before the title.
    author = re.sub(r"^\s*(?:\[\d+\]|\d+[.)])\s*", "", before)
    author = re.split(r",|\s+and\s+|\s+&\s+|\bet al\b|\(?\b(?:19|20)\d{2}", author, maxsplit=1, flags=re.I)[0]
    name = normalize_title(author).split()
    if not name or len(name[-1]) < 2:
        return None
    without_pages = re.sub(r"\bpp?\.\s*\d+(?:\s*[–—-]\s*\d+)?", " ", venue, flags=re.I)
    years = set(re.findall(r"\b(?:19|20)\d{2}\b", before + " " + without_pages))
    if len(years) == 1:
        return name, years.pop(), venue
    return None


def first_author_agrees(printed_name, indexed_name):
    if not indexed_name or printed_name[-1] != indexed_name[-1]:
        return False
    return len(printed_name) == 1 or printed_name[0] in (indexed_name[0], indexed_name[0][0])
