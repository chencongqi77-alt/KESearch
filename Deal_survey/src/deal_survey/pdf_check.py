"""Offline count comparison between PDF citation links and printed Markdown labels."""

from collections import Counter
import re


_LABEL = re.compile(r"\[(\d+)\]")
_GROUP = re.compile(r"\[\s*\d+(?:\s*[,;–—-]\s*\d+)*\s*\]")
_DIGITS = re.compile(r"\d+")
_SCOPE = "Counts only explicitly printed numeric labels and verified cite.* PDF links, by number across the whole document."
_MAX_EXCERPTS_PER_LABEL = 3
_MAX_EXCERPT_CHARS = 480


class _Unverifiable(ValueError):
    """The original PDF does not expose the evidence needed for this comparison."""


def _page_callouts(page, pymupdf):
    # The raw glyph centers disambiguate adjacent lines that overlap the link box.
    # This follows Test01/work_tool/survey_reference_probe.py, and also handles
    # individual visible numbers within a bracketed group.
    flags = pymupdf.TEXTFLAGS_RAWDICT & ~pymupdf.TEXT_PRESERVE_IMAGES
    callouts, boxes = [], []
    for block in page.get_text("rawdict", flags=flags)["blocks"]:
        lines = []
        for line in block.get("lines", []):
            chars = [c for span in line["spans"] for c in span["chars"]]
            text = "".join(c["c"] for c in chars)
            line_box = pymupdf.Rect(line["bbox"])
            boxes.append(line_box)
            lines.append((text, line_box))
            for group in _GROUP.finditer(text):
                for label in _DIGITS.finditer(text, group.start(), group.end()):
                    box = pymupdf.Rect(chars[label.start()]["bbox"])
                    box |= pymupdf.Rect(chars[label.end() - 1]["bbox"])
                    callouts.append((int(label[0]), (box.tl + box.br) / 2, lines, len(lines) - 1))
    return callouts, boxes


def _nearby_lines(upper, lower):
    overlap = min(upper.x1, lower.x1) - max(upper.x0, lower.x0)
    return (upper.y0 < lower.y0 and lower.y0 - upper.y1 <= max(upper.height, lower.height)
            and overlap > min(upper.width, lower.width) / 2)


def _excerpt(callout, boxes, page_number, link_box, pymupdf):
    _, center, lines, index = callout
    if sum(center in box for box in boxes) != 1:
        return None
    text, box = lines[index]
    if len(text) > _MAX_EXCERPT_CHARS:
        return None
    start = end = index
    if index > 0 and _nearby_lines(lines[index - 1][1], box):
        if len(lines[index - 1][0]) + 1 + len(text) <= _MAX_EXCERPT_CHARS:
            start -= 1
    if index + 1 < len(lines) and _nearby_lines(box, lines[index + 1][1]):
        if sum(len(value) + 1 for value, _ in lines[start:index + 2]) - 1 <= _MAX_EXCERPT_CHARS:
            end += 1
    selected = lines[start:end + 1]
    bounds = pymupdf.Rect(box)
    for _, line_box in selected:
        bounds |= line_box
    return {"page": page_number, "rect": [round(x, 2) for x in link_box],
            "quote_rect": [round(x, 2) for x in bounds], "quote": "\n".join(value for value, _ in selected)}


def _read_pdf_links(pdf_path, parsed_numbers):
    import pymupdf

    with pymupdf.open(pdf_path) as pdf:
        if pdf.needs_pass:
            raise _Unverifiable("password_required")
        if not hasattr(pdf, "resolve_names"):
            raise _Unverifiable("named_destination_api_unavailable")
        destinations = {key: value for key, value in pdf.resolve_names().items() if key.startswith("cite.")}
        if not destinations:
            raise _Unverifiable("no_named_citation_destinations")

        numbers = {}
        pages_by_number = {}
        labels_by_page = {}
        for key, dest in destinations.items():
            page_index = dest.get("page")
            if type(page_index) is not int or not 0 <= page_index < len(pdf) or not dest.get("to"):
                raise _Unverifiable("unsupported_citation_destination")
            page = pdf[page_index]
            if page_index not in labels_by_page:
                labels_by_page[page_index] = [(word[0], word[1], int(label[1]))
                    for word in page.get_text("words") if (label := _LABEL.fullmatch(word[4]))]
            point = pymupdf.Point(dest["to"]) * page.transformation_matrix
            # Match the printed bibliography label just below the destination,
            # in its own column. Never assign numbers from bibliography order.
            matches = [number for x, y, number in labels_by_page[page_index]
                       if abs(x - point.x) <= 3 and -1 <= y - point.y <= 8]
            if len(matches) != 1 or matches[0] in pages_by_number:
                raise _Unverifiable("ambiguous_printed_bibliography_label")
            numbers[key] = matches[0]
            pages_by_number[matches[0]] = Counter()

        excerpts = {}
        for page in pdf:
            links = [link for link in page.get_links() if str(link.get("nameddest", "")).startswith("cite.")]
            if not links:
                continue
            callouts, boxes = _page_callouts(page, pymupdf)
            for link in links:
                expected = numbers.get(link["nameddest"])
                visible = [item for item in callouts if item[1] in link["from"]]
                if expected is None or len(visible) != 1 or visible[0][0] != expected:
                    raise _Unverifiable("body_label_and_destination_unconfirmed")
                pages_by_number[expected][page.number + 1] += 1
                if expected not in parsed_numbers:
                    samples = excerpts.setdefault(expected, [])
                    if len(samples) < _MAX_EXCERPTS_PER_LABEL:
                        sample = _excerpt(visible[0], boxes, page.number + 1, link["from"], pymupdf)
                        if sample:
                            samples.append(sample)
        if not any(pages_by_number.values()):
            raise _Unverifiable("no_named_body_citation_links")
        return pages_by_number, excerpts


def check_pdf_citations(pdf_path, references, mentions):
    """Compare explicit labels only. PDF page lists locate links, never a Markdown sentence."""
    report = {"status": "unverified", "scope": _SCOPE, "differences": [], "labels": []}
    if not pdf_path:
        return {**report, "reason": "no_original_pdf"}
    parsed = Counter()
    number_by_id = {ref["id"]: ref["number"] for ref in references
                    if ref.get("id") and type(ref.get("number")) is int}
    mentioned_numbers = set()
    for mention in mentions:
        targets = {t["number"] for t in mention.get("targets", ()) if type(t.get("number")) is int}
        mentioned_numbers.update(targets)
        mentioned_numbers.update(number_by_id[key] for key in mention.get("reference_ids", ()) if key in number_by_id)
        # A [3–5] range visibly prints 3 and 5. Its implied target 4 is useful
        # for a paper's mention list, but is not a printed glyph on the PDF.
        for label in _DIGITS.findall(mention.get("marker", "")):
            if int(label) in targets:
                parsed[int(label)] += 1
    try:
        pdf_pages, excerpts = _read_pdf_links(pdf_path, mentioned_numbers)
    except ImportError:
        return {**report, "reason": "pymupdf_unavailable"}
    except _Unverifiable as error:
        return {**report, "reason": str(error)}
    except (OSError, RuntimeError, TypeError, ValueError, KeyError, IndexError):
        return {**report, "reason": "unreadable_or_unsupported_pdf"}

    bibliography = Counter(ref["number"] for ref in references if type(ref.get("number")) is int)
    if not bibliography:
        return {**report, "reason": "no_parsed_numeric_bibliography"}
    if any(count > 1 for count in bibliography.values()):
        return {**report, "reason": "ambiguous_parsed_bibliography_numbers"}

    for number in sorted(pdf_pages.keys() | parsed.keys() | bibliography.keys()):
        pages = pdf_pages.get(number, {})
        row = {"label": number, "pdf_count": sum(pages.values()), "parsed_count": parsed[number],
               "pdf_pages": sorted(pages)}
        report["labels"].append(row)
        if row["pdf_count"] != row["parsed_count"]:
            if row["parsed_count"] == 0 and number not in mentioned_numbers:
                row = {**row, "pdf_excerpts": excerpts.get(number, [])}
            report["differences"].append(row)
    report.update(status="differences" if report["differences"] else "matched",
                  pdf_count=sum(sum(pages.values()) for pages in pdf_pages.values()),
                  parsed_count=sum(parsed.values()))
    return report
