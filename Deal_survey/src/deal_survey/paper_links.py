"""Bounded, identity-checked DOI lookup for bibliography entries without a direct link."""

from __future__ import annotations

import http.client
import json
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import build_opener, HTTPRedirectHandler, Request

from .citation_identity import normalize_title, title_identity_key


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_bounded(request, *, timeout, limit):
    with build_opener(_NoRedirect()).open(request, timeout=timeout) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("服务响应超出大小限制")
    return raw


_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
_YEAR = re.compile(r"\b((?:18|19|20)\d{2})[a-z]?\b", re.I)
_VOLUME = re.compile(r"\bvol(?:ume)?\.?\s*(\d+)\b", re.I)
_ISSUE = re.compile(r"\b(?:no|issue)\.?\s*(\d+(?:\s*[-–—/]\s*\d+)?)\b", re.I)
_PAGE_RANGE = re.compile(r"([a-z]?\d+)(?:\s*[-–—]\s*([a-z]?\d+))?", re.I)
_SELECT = ("DOI,title,subtitle,author,issued,published-print,published-online,type,container-title,"
           "short-container-title,volume,issue,page,article-number,publisher,ISSN,relation")
_pool = threading.Lock()
_next_query = 0.0


def _citation(ref):
    if ref["link_kind"] != "arxiv_search":
        return None
    title, entry = ref["title"], ref["entry"]
    if title == entry or not 5 <= len(title) <= 300:
        return None
    normal = normalize_title(title)
    if len(normal.split()) < 2:
        return None
    match = re.search(r"\s+".join(map(re.escape, title.split())), entry, re.I)
    if match is None:
        return None
    authors = entry[:match.start()]
    if not any(len(word) > 1 and word.isalpha() for word in normalize_title(authors).split()):
        return None
    years = set(_YEAR.findall(authors + " " + entry[match.end():]))
    return title, authors, years


def _pages(value):
    match = _PAGE_RANGE.fullmatch(str(value).strip().casefold())
    if not match:
        return None
    start, end = match.groups()
    if end and start.isdigit() and end.isdigit() and len(end) < len(start):
        end = start[:-len(end)] + end
    return start, end


def _publication(ref):
    # Source metadata follows the title. "in <proceedings>, vol..." is a different
    # bibliographic convention from "<journal>, vol..., no..., pp...".
    entry, title = ref["entry"], ref["title"]
    pos = entry.find(title)
    tail = entry[pos + len(title):].lstrip(' ,.;:，。”’"') if pos >= 0 else ""
    volume = _VOLUME.search(tail)
    journal = ""
    if volume:
        prefix = tail[:volume.start()].strip(" ,.;")
        if 2 < len(prefix) < 150 and not re.search(r"^(?:in\b|proc\b)|\b(?:proceedings|conference|workshop)\b", prefix, re.I):
            journal = normalize_title(prefix)
    page = re.search(r"\bpp?\.?\s*(" + _PAGE_RANGE.pattern + r")(?=\s*[,.;]|\s*$)", tail, re.I)
    issue = _ISSUE.search(tail)
    return (journal, volume[1] if volume else "", issue[1] if issue else "", _pages(page[1]) if page else None)


def _listed_years(row):
    listed = set()
    for field in ("issued", "published-online", "published-print"):
        value = row.get(field)
        parts = value.get("date-parts") if isinstance(value, dict) else None
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            listed.add(str(parts[0][0]))
    return listed


def _issue_numbers(value):
    if not isinstance(value, str):
        return set()
    bounds = re.fullmatch(r"(\d+)(?:\s*[-–—/]\s*(\d+))?", value)
    if not bounds:
        return set()
    start, end = int(bounds[1]), int(bounds[2] or bounds[1])
    return set(range(start, end + 1)) if 0 <= end - start <= 50 else set()


def _containers(row):
    names = set()
    for field in ("container-title", "short-container-title"):
        values = row.get(field)
        if isinstance(values, list):
            names.update(normalize_title(value) for value in values if isinstance(value, str))
    return names


def _compatible(row, location):
    journal, volume, issue, pages = location
    if journal:
        if row.get("type") and row["type"] != "journal-article":
            return False
        names = _containers(row)
        if names and journal not in names:
            return False
        if row.get("volume") and str(row["volume"]) != volume:
            return False
        deposited_issue = _issue_numbers(row.get("issue"))
        if issue and deposited_issue and _issue_numbers(issue).isdisjoint(deposited_issue):
            return False
    printed = _pages(row.get("page") or row.get("article-number") or "")
    if pages and printed:
        if pages[0] != printed[0] or (pages[1] and printed[1] and pages[1] != printed[1]):
            return False
    return True


def _authors_signature(row, authors):
    # Match the whole printed author list in order, permitting only full names
    # or their printed initials. An "et al." entry cannot establish this identity.
    remaining = re.sub(r"^\d+\s+", "", authors)
    remaining = re.sub(r"\s+(?:18|19|20)\d\d[a-z]?$", "", remaining)
    signature = []
    for person in row["author"]:
        if not isinstance(person, dict) or not isinstance(person.get("family"), str) or not isinstance(person.get("given"), str):
            return None
        family = normalize_title(person["family"])
        given = normalize_title(person["given"])
        if not family or not given:
            return None
        initials = " ".join(part[0] for part in given.split())
        options = {v for name in (given, initials, initials.replace(" ", ""))
                   for v in (name + " " + family, family + " " + name)}
        remaining = remaining.removeprefix("and ")
        matched = next((v for v in sorted(options, key=len, reverse=True)
                        if remaining == v or remaining.startswith(v + " ")), None)
        if not matched:
            return None
        remaining = remaining[len(matched):].lstrip()
        signature.append((given, family))
    return tuple(signature) if not remaining else None


def _single_journal_location(matches, authors, years, location):
    journal, volume, _, pages = location
    if not (journal and volume and pages and pages[1] and years):
        return False
    signatures = set()
    shared_issns, shared_years = None, set(years)
    for row in matches.values():
        author_key = _authors_signature(row, authors)
        publisher = row.get("publisher")
        issns = row.get("ISSN")
        if (row.get("type") != "journal-article" or journal not in _containers(row)
                or row.get("volume") != volume or _pages(row.get("page")) != pages
                or not author_key or not isinstance(publisher, str) or not publisher.strip()
                or not isinstance(issns, list)):
            return False
        identifiers = {value for value in issns if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{3}[\dX]", value, re.I)}
        shared_issns = identifiers if shared_issns is None else shared_issns & identifiers
        shared_years &= _listed_years(row)
        signatures.add((normalize_title(publisher), author_key))
    return len(signatures) == 1 and bool(shared_issns and shared_years)


def _identical_relations(matches):
    # Crossref is-identical-to is symmetric. It does not specify a primary DOI.
    edges = {doi: set() for doi in matches}
    for doi, row in matches.items():
        relation = row.get("relation")
        entries = relation.get("is-identical-to") if isinstance(relation, dict) else None
        for item in entries if isinstance(entries, list) else ():
            if not isinstance(item, dict) or item.get("id-type") != "doi" or not isinstance(item.get("id"), str):
                continue
            other = item["id"].casefold().removeprefix("https://doi.org/")
            if other in edges:
                edges[doi].add(other)
                edges[other].add(doi)
    reached, pending = set(), [next(iter(matches))]
    while pending:
        current = pending.pop()
        if current not in reached:
            reached.add(current)
            pending.extend(edges[current] - reached)
    return reached == set(matches)


def _match_records(rows, title, authors, years, location):
    matches = {}
    title_key = title_identity_key(title)
    first = re.split(r",|\s+and\s+|\s*&\s*|\bet al\b", authors, maxsplit=1, flags=re.I)[0]
    first_words = [word for word in normalize_title(first).split() if word.isalpha()]
    while first_words and len(first_words[-1]) == 1:
        first_words.pop()
    printed_author = " " + " ".join(first_words)
    for row in rows:
        if not isinstance(row, dict):
            continue
        doi = row.get("DOI")
        titles = row.get("title")
        if (not isinstance(doi, str) or len(doi) > 300 or not _DOI.fullmatch(doi)
                or not isinstance(titles, list) or not titles or not isinstance(titles[0], str)):
            continue
        variants = [titles[0]]
        subtitles = row.get("subtitle")
        if isinstance(subtitles, list) and subtitles and isinstance(subtitles[0], str) and subtitles[0].strip():
            if not title_identity_key(titles[0]).endswith(title_identity_key(subtitles[0])):
                # The metadata supplies an explicit title/subtitle boundary.
                variants = [titles[0] + sep + subtitles[0] for sep in (" ", ": ", ". ", " — ")]
        supported = [value for value in variants if title_identity_key(value) == title_key]
        needs_ocr_join = not any(normalize_title(value) == normalize_title(title) for value in supported)
        if not supported or (needs_ocr_join and len(title_key) < 16):
            continue
        people = row.get("author")
        if not isinstance(people, list) or not people or not isinstance(people[0], dict):
            continue
        family = people[0].get("family")
        if not isinstance(family, str):
            continue
        family = normalize_title(family)
        if len(family) < 2 or not printed_author.endswith(" " + family):
            continue
        listed = _listed_years(row)
        if needs_ocr_join and not (years & listed):
            continue
        if (years and listed and years.isdisjoint(listed)) or not _compatible(row, location):
            continue
        matches[doi.casefold()] = row
    if not matches:
        return "not_found", None, []
    if len(matches) == 1:
        return "matched", "crossref_title_author", sorted(matches)
    if _identical_relations(matches):
        return "matched", "crossref_identical_relation", sorted(matches)
    if _single_journal_location(matches, normalize_title(authors), years, location):
        return "matched", "crossref_journal_location", sorted(matches)
    return "ambiguous", None, []


def resolve_publication_links(catalogue, *, max_seconds=30):
    """Resolve Crossref publication links and retain the per-entry outcome for another pass."""
    global _next_query
    deadline = time.monotonic() + max_seconds
    pending = []
    for ref in catalogue.values():
        if ref["link_kind"] != "arxiv_search":
            continue
        checks = ref.setdefault("link_checks", {})
        citation = _citation(ref)
        if citation:
            prior = checks.setdefault("crossref", "not_attempted")
            # Give a short retry budget to unvisited entries before repeating known misses.
            history = ref.get("link_checked_at", {}).get("crossref", 0)
            priority = (prior != "not_attempted", history if isinstance(history, (float, int)) else 0)
            pending.append((priority, ref, citation))
        else:
            checks["crossref"] = "insufficient_metadata"
    for _, ref, citation in sorted(pending, key=lambda item: item[0]):
        checks = ref["link_checks"]
        if not _pool.acquire(timeout=max(0, deadline - time.monotonic())):
            return
        try:
            delay = max(0, _next_query - time.monotonic())
            remaining = deadline - time.monotonic() - delay
            if remaining < 1:
                return
            if delay:
                time.sleep(delay)
            # Crossref's public works search pool permits one simultaneous request and one start/second.
            _next_query = time.monotonic() + 1.05
            title, authors, years = citation
            params = urlencode({"query.bibliographic": (ref["title"] + " " + normalize_title(authors)[:100]).strip(),
                                "rows": 8, "select": _SELECT})
            request = Request("https://api.crossref.org/works?" + params,
                              headers={"Accept": "application/json", "User-Agent": "KESearch-SurveyReader/1.0"})
            ref.setdefault("link_checked_at", {})["crossref"] = time.time()
            payload = json.loads(fetch_bounded(request, timeout=min(5, remaining), limit=512 * 1024))
            if not isinstance(payload, dict) or payload.get("status") != "ok":
                raise ValueError("invalid works response")
            message = payload.get("message")
            rows = message.get("items") if isinstance(message, dict) else None
            if not isinstance(rows, list):
                raise ValueError("invalid works list")
            outcome, evidence, dois = _match_records(rows, title, authors, years, _publication(ref))
            checks["crossref"] = outcome
            if dois:
                urls = ["https://doi.org/" + quote(doi, safe="/():;-._") for doi in dois]
                ref.update(link_kind="doi", url=urls[0], link_evidence=evidence)
                if len(urls) > 1:
                    ref["alternate_urls"] = urls[1:]
        except HTTPError as error:
            checks["crossref"] = "rate_limited" if error.code == 429 else "unavailable"
            if error.code == 429:
                retry = error.headers.get("Retry-After", "") if error.headers else ""
                cooldown = int(retry) if re.fullmatch(r"\d{1,7}", retry) else 60
                _next_query = max(_next_query, time.monotonic() + cooldown)
            return
        except (OSError, URLError, http.client.HTTPException, ValueError):
            checks["crossref"] = "unavailable"
            return
        finally:
            _pool.release()
