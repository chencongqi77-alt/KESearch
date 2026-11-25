"""Locate survey passages in the ordered MinerU v1 blocks and the PDF outline."""
from __future__ import annotations

from collections import defaultdict
import re
import unicodedata

from pypdf import PdfReader

from .citations import BACK_HEADING, REF_HEADING


NUMBER = re.compile(r"^\s*(?:section\s+)?(\d{1,3}(?:\.\d{1,3})*)[.)]?\s+(?=\S)", re.I)
COMMON_HEADING = re.compile(r"^(?:abstract|summary|introduction|background|related work|contents|摘要|引言|绪论)$", re.I)
TABLE_ROW = re.compile(r"<tr\b[^>]*>.*?</tr\s*>", re.I | re.S)


def _key(text):
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


def pdf_outline(path):
    """Return title and (level, title, one-based physical page) bookmark rows."""
    warnings = []
    rows = []
    title = None
    with open(path, "rb") as source:
        reader = PdfReader(source)
        try:
            title = reader.metadata.title if reader.metadata else None
            pending = [(iter(reader.outline), 1)]
            while pending:
                entries, level = pending[-1]
                item = next(entries, None)
                if item is None:
                    pending.pop()
                elif isinstance(item, list):
                    pending.append((iter(item), level + 1))
                else:
                    page = reader.get_destination_page_number(item)
                    if page is not None and page >= 0 and item.title:
                        rows.append((level, str(item.title), page + 1))
        except Exception as exc:
            # The page stream may be valid even when the optional outline is corrupt.
            warnings.append({"code": "pdf_outline_unreadable", "detail": type(exc).__name__})
    return title, rows, warnings


def _level(title, mineru_level, bookmark, offset):
    if bookmark:
        return bookmark[0], "pdf_bookmark"
    number = NUMBER.match(title)
    if number:
        return number[1].count(".") + 1, "printed_section_number"
    if re.match(r"^[IVXLCDM]+\.\s+\S", title):
        return 1, "printed_roman_number"
    if re.match(r"^[A-Z]\.\s+\S", title):
        return 2, "printed_subsection_letter"
    return max(1, (mineru_level or 1) - offset), "mineru_heading"


def _fields(block):
    kind = block.get("type")
    if kind in {"text", "title", "heading", "aside_text", "page_footnote", "footnote"}:
        fields = ["text"]
    elif kind == "list":
        fields = ["list_items"]
    elif kind in {"image", "chart", "table"}:
        fields = [kind + "_caption", kind + "_footnote"]
        if kind == "table":
            fields.append("table_body")
    else:
        return
    for field in fields:
        value = block.get(field)
        if isinstance(value, str) and value.strip():
            if field == "table_body":
                rows = list(TABLE_ROW.finditer(value))
                if rows:
                    for row in rows:
                        yield field, row.group(), row.start()
                    continue
            yield field, value, 0
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str) and item.strip():
                    yield f"{field}[{index}]", item, 0


def locate_passages(blocks, bibliography, outline=(), pdf_title=None):
    """Assign each evidence unit to its deepest observed heading, in reading order."""
    bookmarks = defaultdict(list)
    for level, text, page in outline:
        bookmarks[(page, _key(text))].append((level, text))
    root = {"id": "document", "parent_id": None, "level": 0, "title": pdf_title or "",
            "page": 1, "block_index": None, "basis": "document", "path": []}
    stack, sections, units, diagnostics = [root], [root], [], []
    offset = 0
    in_references = False
    for index, block in enumerate(blocks):
        text = (block.get("text") or "").strip() if isinstance(block.get("text"), str) else ""
        idx = block.get("page_idx")
        page = idx + 1 if type(idx) is int and idx >= 0 else None
        matches = bookmarks.get((page, _key(text)), ()) if text else ()
        bookmark = matches[0] if len(matches) == 1 else None
        level = block.get("text_level")
        level = level if type(level) is int and level > 0 else None
        marked = level is not None or block.get("type") in {"title", "heading"}
        # Keep bibliography text out of citations but retain its header for navigation.
        ref_heading = bool(REF_HEADING.fullmatch(text))
        heading = ((marked or bookmark or ref_heading or BACK_HEADING.fullmatch(text))
                   and text and block.get("type") in {"text", "title", "heading"})
        if heading:
            in_references = ref_heading
            document_title = index <= 2 and page in (1, None) and root["block_index"] is None and len(sections) == 1
            if (document_title and not bookmark and not NUMBER.match(text) and not ref_heading
                    and not COMMON_HEADING.fullmatch(text)
                    and (_key(text) == _key(pdf_title or "") or (index == 0 and (level == 1 or block.get("type") == "title")))):
                root.update(title=text, block_index=index, basis="document_title")
                offset = 1 if level == 1 else 0
                continue
            depth, basis = _level(text, level, bookmark, offset)
            while len(stack) > 1 and stack[-1]["level"] >= depth:
                stack.pop()
            # A missing intermediate heading must not attach 3.2 to chapter 2.
            number = NUMBER.match(text)
            while number and len(stack) > 1:
                parent_number = NUMBER.match(stack[-1]["title"])
                if not parent_number or number[1].startswith(parent_number[1] + "."):
                    break
                stack.pop()
            parent = stack[-1]
            if depth > parent["level"] + 1:
                diagnostics.append({"code": "heading_level_gap", "block_index": index, "title": text})
            section = {"id": f"section-{len(sections):03}", "parent_id": parent["id"], "level": depth,
                       "title": text, "page": page, "block_index": index, "basis": basis,
                       "path": [*parent["path"], text]}
            sections.append(section)
            stack.append(section)
        if in_references or index in bibliography:
            continue
        for field, value, field_offset in _fields(block):
            units.append({"section_id": stack[-1]["id"], "page": page, "block_index": index,
                          "field": field, "field_offset": field_offset, "text": value})
    if len(sections) == 1:
        diagnostics.append({"code": "no_section_headings"})
    return sections, units, diagnostics
