"""Last-pass lookup for articles omitted from DOI and preprint indexes."""
from __future__ import annotations

from http.client import HTTPException
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request

from .citation_identity import cited_metadata, first_author_agrees, normalize_title, title_identity_key
from .paper_links import fetch_bounded


_next_request = 0.0
_EDITION_PATHS = {
    "aclanthology.org": r"/(?:[A-Z]\d{2}-\d+|\d{4}\.[\w.-]+)/?",
    "proceedings.mlr.press": r"/v\d+/[\w-]+\.html",
    "proceedings.neurips.cc": r"/(?:paper|paper_files/paper)/\d{4}/hash/[a-f0-9]+-Abstract(?:-[\w-]+)?\.html",
    "openaccess.thecvf.com": r"/content[\w./-]+\.html",
}


def _article_link(work):
    loc = work.get("primary_location") or {}
    for raw in (work.get("doi"), loc.get("landing_page_url"), loc.get("pdf_url")):
        if not isinstance(raw, str) or re.search(r"[\s\\\x00-\x1f]", raw):
            continue
        try:
            url = urlsplit(raw)
            if url.scheme not in ("http", "https") or url.username or url.password or url.port not in (None, 443):
                continue
        except ValueError:
            continue
        host, path = url.hostname, url.path
        if host == "doi.org" and re.fullmatch(r"/10\.\d{4,9}/[-._;()/:A-Z0-9]+", path, re.I):
            return "doi", "https://doi.org" + path
        if host == "arxiv.org" and re.fullmatch(r"/abs/(?:\d{4}\.\d{4,5}|[a-z][\w.-]+/\d{7})(?:v\d+)?", path, re.I):
            return "arxiv", "https://arxiv.org" + path
        # Retain a record's specific electronic edition. Never turn a journal homepage into a paper link.
        if host in {"wseas.us", "www.wseas.us", "wseas.org", "www.wseas.org"}:
            if re.fullmatch(r"/(?:e-library|multimedia)/[\w./%~-]+\.pdf", path, re.I) and ".." not in path:
                return "source", "https://" + host + path
        if host in _EDITION_PATHS and re.fullmatch(_EDITION_PATHS[host], path) and ".." not in path:
            return "source", "https://" + host + path
    return None


def _match(ref, metadata, payload):
    rows = payload["results"]
    if not isinstance(rows, list):
        raise ValueError("invalid works list")
    if payload["meta"]["count"] > len(rows):
        return "incomplete"
    title = title_identity_key(ref["title"])
    author, year, venue = metadata
    printed_volume = re.search(r"\bvol(?:ume)?\.?\s+(\d+)\b", venue, re.I)
    printed_page = re.search(r"\bpp?\.\s*(\d+(?: \d{3})*)", venue, re.I)
    matches = {}
    for work in rows:
        if (not re.fullmatch(r"https://openalex\.org/W\d+", str(work.get("id"))) or not isinstance(work.get("title"), str)
                or title_identity_key(work["title"]) != title or str(work.get("publication_year")) != year):
            continue
        biblio = work.get("biblio") or {}
        if printed_volume and biblio.get("volume") and printed_volume[1] != str(biblio["volume"]):
            continue
        if printed_page and biblio.get("first_page") and printed_page[1].replace(" ", "") != str(biblio["first_page"]):
            continue
        authors = work.get("authorships") or []
        if not authors:
            continue
        first = (authors[0].get("author") or {}).get("display_name") or ""
        if first_author_agrees(author, normalize_title(first).split()):
            matches[work["id"]] = _article_link(work)
    if len(matches) > 1:
        return "ambiguous"
    link = next(iter(matches.values()), None)
    if link:
        ref.update(link_kind=link[0], url=link[1], link_evidence="openalex_title_author_year",
                   link_record=next(iter(matches)))
        return "matched"
    return "not_found"


def resolve_openalex_links(catalogue, *, max_seconds=12):
    global _next_request
    deadline = time.monotonic() + max_seconds
    for ref in catalogue.values():
        if ref.get("link_kind") != "arxiv_search":
            continue
        checks = ref.setdefault("link_checks", {})
        metadata = cited_metadata(ref)
        if not metadata:
            checks["openalex"] = "insufficient_metadata"
            continue
        checks.setdefault("openalex", "not_attempted")
        delay = max(0.0, _next_request - time.monotonic())
        remaining = deadline - time.monotonic() - delay
        if remaining < 0.75:
            break
        if delay:
            time.sleep(delay)
        _next_request = time.monotonic() + 1
        query = urlencode({"filter": "title.search:" + normalize_title(ref["title"]) + ",publication_year:" + metadata[1],
                           "per_page": 12, "select": "id,doi,title,publication_year,authorships,biblio,primary_location"})
        request = Request("https://api.openalex.org/works?" + query, headers={"User-Agent": "KESearch-SurveyReader/1.0"})
        ref.setdefault("link_checked_at", {})["openalex"] = time.time()
        try:
            payload = json.loads(fetch_bounded(request, timeout=min(5, remaining), limit=2 * 1024 * 1024))
            checks["openalex"] = _match(ref, metadata, payload)
        except HTTPError as error:
            checks["openalex"] = "rate_limited" if error.code == 429 else "unavailable"
            if error.code == 429:
                retry = error.headers.get("Retry-After", "") if error.headers else ""
                _next_request = time.monotonic() + (int(retry) if re.fullmatch(r"\d{1,7}", retry) else 60)
            break
        except (OSError, URLError, ValueError, HTTPException, KeyError, TypeError, AttributeError):
            checks["openalex"] = "unavailable"
            break
