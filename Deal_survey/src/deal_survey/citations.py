"""Link survey citation markers to local bibliography entries and verbatim discussion."""
from __future__ import annotations

from collections import defaultdict
import re
import unicodedata

REF_HEADING = re.compile(
    r"(?:#{1,6}\s*)?(?:(?:\d+(?:\.\d+)*|[IVXLCDM]+)[.)]?\s+)?"
    r"(?:references(?: and notes)?|bibliography|literature cited|works cited|参考文献|參考文獻)\s*[:：]?", re.I)
BACK_HEADING = re.compile(
    r"(?:appendi(?:x|ces)(?:\s+[A-Z0-9]+)?|supplementary materials?|acknowledg[e]?ments?|"
    r"author biographies|附录(?:\s*[A-Z0-9])?|致谢)(?:\s*[:：]\s*.+)?", re.I)
LABEL = re.compile(r"^[ \t]*(?:[\[［]([1-9]\d{0,3})[\]］]|([1-9]\d{0,3})[.)](?=\s)|([1-9]\d{0,2})(?=\s+[A-Z]))[ \t]*", re.M)
YEAR = r"(?:18|19|20)\d\d[a-z]?"
YEAR_TOKEN = re.compile(r"\b" + YEAR + r"\b")
NAME = r"(?:[A-ZÀ-ÖØ-Þ][^\W\d_]*(?:[-'’][^\W\d_]+)*)"
AUTHOR = rf"(?P<author>{NAME})(?:\s+et\s+al\.?|\s+(?:and|&)\s+(?P<coauthor>{NAME}))?"
YEARS = rf"(?P<years>{YEAR}(?:,\s*{YEAR})*)"
PAREN_AUTHOR = re.compile(rf"{AUTHOR}\s*,?\s+{YEARS}")
NARRATIVE = re.compile(rf"(?<![\w’'-]){AUTHOR}\s*\(\s*{YEARS}\s*\)")
PAREN = re.compile(r"\(([^()\n]{1,800})\)")
# Adapted from Test01/work_tool/provenance.py. Keep its formula/code exclusions
# and grouped citation grammar, with four digits for larger survey bibliographies.
NUMBER = r"[1-9][0-9]{0,3}"
RANGE = rf"{NUMBER}(?:\s*[-–—]\s*{NUMBER})?"
NUMERIC = re.compile(rf"(?<![\w\\_{{])\[({RANGE}(?:\s*[,;]\s*{RANGE})*)\]"
                     rf"(?:\s*[-–—]\s*\[({NUMBER})\])?")
MATH_OR_CODE = re.compile(r"\$\$[\s\S]*?\$\$|(?<!\\)\$(?:\\.|[^$\\\n])*\$|"
                          r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|(?P<ticks>`+)[\s\S]*?(?P=ticks)")
SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[\u3400-\u9fff])|(?<=[。！？])")
WORD = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")


def _typed(block):
    return block.get("type") == "ref_text" or block.get("sub_type") == "ref_text"


def bibliography_indices(blocks):
    """Indices of bibliography headings and entries, excluding later appendices."""
    result = {i for i, block in enumerate(blocks) if _typed(block)}
    heading = None
    for i in range(len(blocks) + 1):
        block = blocks[i] if i < len(blocks) else {}
        text = block.get("text", "")
        is_reference = isinstance(text, str) and REF_HEADING.fullmatch(text.strip())
        is_heading = (block.get("text_level") or block.get("type") in {"title", "heading"}
                      or (isinstance(text, str) and BACK_HEADING.fullmatch(text.strip())))
        if i == len(blocks) or is_heading or is_reference:
            if heading is not None:
                has_typed = any(_typed(b) for b in blocks[heading + 1:i])
                for j in range(heading + 1, i):
                    item = blocks[j]
                    if item.get("type") in {"text", "list"} and (
                            not has_typed or LABEL.match(str(item.get("text", "")))):
                        result.add(j)
            heading = i if is_reference else None
            if is_reference:
                result.add(i)
    return result


def _pieces(blocks, indices):
    for index in sorted(indices):
        block = blocks[index]
        fields = [("text", block.get("text"))]
        if isinstance(block.get("list_items"), list):
            fields.extend((f"list_items[{j}]", text) for j, text in enumerate(block["list_items"]))
        for field, text in fields:
            if not isinstance(text, str) or not text.strip() or REF_HEADING.fullmatch(text.strip()):
                continue
            starts = [m.start() for m in LABEL.finditer(text)]
            boundaries = sorted({0, *starts, len(text)})
            for begin, end in zip(boundaries, boundaries[1:]):
                raw = text[begin:end]
                entry = raw.strip()
                if not entry:
                    continue
                start = begin + len(raw) - len(raw.lstrip())
                match = LABEL.match(entry)
                number = int(next(g for g in match.groups() if g)) if match else None
                page_idx = block.get("page_idx")
                yield number, entry, {"block_index": index, "field": field,
                    "page": page_idx + 1 if type(page_idx) is int else None,
                    "start": start, "end": start + len(entry)}


def _key(name):
    return "".join(c for c in unicodedata.normalize("NFKD", name.casefold()) if c.isalpha())


def _author_info(entry):
    """Return keys for conservative author–year matching within this bibliography."""
    body = LABEL.sub("", entry, count=1)
    explicit_year = re.search(r"(?:^|[.\s,])\(?(" + YEAR + r")\)?[.,]\s+", body)
    quoted = re.search(r'[“"]([^”"\n]+)[”"]', body)
    year = explicit_year[1] if explicit_year else None
    authors = body[:explicit_year.start()] if explicit_year else body
    if quoted:
        authors = body[:quoted.start()]
    # Some styles put the year at the end. Stop before the title when
    # collecting author keys, so words in the title cannot match a coauthor.
    authors = re.split(r"(?<=[a-zà-öø-ÿ])\.\s+(?=[A-ZÀ-ÖØ-Þ])", authors, maxsplit=1)[0]
    if not explicit_year:
        years = list(YEAR_TOKEN.finditer(body))
        if years and len({m[0] for m in years}) == 1:
            year = years[0][0]
    first = re.split(r",|\s+and\s+|\s+&\s+", authors, maxsplit=1)[0].strip()
    words = WORD.findall(first)
    # Inverted forms start "Surname, Initials"; direct forms end in the surname.
    surname = words[-1] if 0 < len(words) <= 7 else None
    if surname and len(surname) == 1 and words:
        surname = words[0]  # Smith J., ...
    title = quoted[1].strip().rstrip(",.") if quoted else None
    title_after_year = re.search(r"(?:\.\s+" + YEAR + r"|\(" + YEAR + r"\))\.\s+", body)
    if not title and title_after_year:
        tail = body[title_after_year.end():].strip()
        title_end = re.search(r"(?<=[a-zA-Z0-9)])\.(?=\s|$)", tail)
        if title_end:
            title = tail[:title_end.start()]
    return _key(surname or ""), year, {_key(w) for w in WORD.findall(authors)}, title


def _references(blocks, indices):
    references = []
    parts = list(_pieces(blocks, indices))
    numbered = sum(number is not None for number, _, _ in parts)
    # Typed reference text may continue across a page break in a numbered list.
    # Only merge a label-free fragment when numbers predominate and the entries
    # on either side show consecutive labels (or the bibliography has ended).
    for index, (number, entry, span) in enumerate(parts):
        previous = references[-1] if references else None
        next_number = parts[index + 1][0] if index + 1 < len(parts) else None
        if (number is None and previous and previous["number"] is not None
                and numbered > len(parts) / 2 and _typed(blocks[span["block_index"]])
                and (next_number == previous["number"] + 1 or index == len(parts) - 1)
                and not previous["entry"].endswith((".", "。"))):
            previous["entry"] += "\n" + entry
            previous["source_spans"].append(span)
        else:
            references.append({"id": f"ref-{len(references) + 1:04d}", "number": number,
                               "entry": entry, "source_spans": [span]})
    return references


def _number_values(match):
    members = re.split(r"[,;]", match[1])
    if match[2]:
        if len(members) != 1 or not members[0].isdigit():
            return []
        members = [members[0] + "-" + match[2]]
    numbers = []
    for member in members:
        bounds = [int(n) for n in re.split(r"[-–—]", member)]
        if not 0 <= bounds[-1] - bounds[0] < 1000:
            return []
        numbers.extend(range(bounds[0], bounds[-1] + 1))
    return list(dict.fromkeys(numbers))


def _target(ids, **key):
    return {**key, "status": "matched" if len(ids) == 1 else "ambiguous" if ids else "unresolved",
            "candidate_ids": list(ids)}


def _author_calls(text):
    for m in NARRATIVE.finditer(text):
        yield m.start(), m.end(), m
    for paren in PAREN.finditer(text):
        # Semicolon-separated authors have distinct precise anchors inside the parentheses.
        for m in PAREN_AUTHOR.finditer(text, paren.start(1), paren.end(1)):
            before = text[paren.start(1):m.start()].rsplit(";", 1)[-1].strip()
            if before.casefold() in {"", "e.g.,", "e.g.", "see", "see also", "cf."}:
                yield m.start(), m.end(), m


def _context(text, start, end, boundaries):
    left = max((hi for _, hi in boundaries if hi <= start), default=0)
    right = next((lo for lo, _ in boundaries if lo >= end), len(text))
    return text[left:right], left, right


def _markers(unit, by_number, by_author):
    text = unit["text"]
    visible = MATH_OR_CODE.sub(lambda m: " " * len(m[0]), text)
    visible = re.sub(r"<[^<>\n]+>", lambda m: " " * len(m[0]), visible)
    markers = []
    numeric_text = visible.translate(str.maketrans("［］，；", "[],;"))
    # CJK text normally attaches a citation directly to the preceding word.
    # Use an equal-length shadow so all offsets still index the original field.
    numeric_text = re.sub(r"[\u3400-\u9fff](?=\[\d)", " ", numeric_text)
    for m in NUMERIC.finditer(numeric_text):
        if numeric_text[m.end():].startswith("("):  # Markdown link label
            continue
        values = _number_values(m)
        targets = [_target(by_number.get(n, []), number=n) for n in values]
        if not values:
            targets = [_target([], reason="invalid_or_large_range")]
        markers.append((m.start(), m.end(), "numeric", targets))
    for start, end, m in _author_calls(visible):
        author, coauthor = _key(m["author"]), _key(m["coauthor"] or "")
        targets = []
        for year in YEAR_TOKEN.findall(m["years"]):
            ids = [rid for rid, words in by_author.get((author, year), []) if not coauthor or coauthor in words]
            targets.append(_target(ids, author=m["author"], year=year))
        markers.append((start, end, "author_year", targets))
    return sorted(markers, key=lambda marker: marker[:2])


def build_citations(blocks, units):
    """Offsets are half-open Unicode indices in the original MinerU text field."""
    indices = bibliography_indices(blocks)
    references = _references(blocks, indices)
    by_number, by_author = defaultdict(list), defaultdict(list)
    for ref in references:
        surname, year, author_words, ref["title"] = _author_info(ref["entry"])
        if ref["number"] is not None:
            by_number[ref["number"]].append(ref["id"])
        if surname and year:
            by_author[surname, year].append((ref["id"], author_words))

    mentions = []
    for unit in units:
        if unit["block_index"] in indices:
            continue
        text = unit["text"]
        boundaries = [(m.start(), m.end()) for m in SENTENCE_BREAK.finditer(text)
                      if not re.search(r"(?i)(?:\bet al|\be\.g|\bi\.e|\bfig|\beq|\b[A-Z])\.$",
                                       text[max(0, m.start() - 8):m.start()])]
        for start, end, style, targets in _markers(unit, by_number, by_author):
            context, left, right = _context(text, start, end, boundaries)
            reference_ids = list(dict.fromkeys(t["candidate_ids"][0] for t in targets if t["status"] == "matched"))
            statuses = {t["status"] for t in targets}
            mentions.append({"id": f"mention-{len(mentions) + 1:04d}",
                **{key: unit[key] for key in ("section_id", "block_index", "field", "page")},
                "field_offset": unit.get("field_offset", 0),
                "start": start, "end": end, "marker": text[start:end], "style": style,
                "context_start": left, "context_end": right, "context": context, "targets": targets,
                "status": next(iter(statuses)) if len(statuses) == 1 else "partial",
                "reference_ids": reference_ids})

    diagnostics = [{"code": "duplicate_reference_number", "number": n, "reference_ids": ids}
                   for n, ids in by_number.items() if len(ids) > 1]
    if not references:
        diagnostics.append({"code": "no_bibliography_entries"})
    if not mentions:
        diagnostics.append({"code": "no_recognized_body_markers"})
    return {"references": references, "mentions": mentions, "diagnostics": diagnostics}
