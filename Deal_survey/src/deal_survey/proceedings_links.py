"""Match unresolved CS papers against entries in their cited official proceedings."""
from __future__ import annotations

from collections import defaultdict
from html.parser import HTMLParser
from http.client import HTTPException
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request
from xml.etree import ElementTree

from .citation_identity import cited_metadata, first_author_agrees, title_identity_key
from .paper_links import fetch_bounded, normalize_title


NEURIPS = "proceedings.neurips.cc"
PMLR = "proceedings.mlr.press"
ACL = "aclanthology.org"
ACL_COLLECTIONS = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/"
_pause_until = {}


def _index_for(ref):
    metadata = cited_metadata(ref)
    if not metadata:
        return None
    name, year, venue = metadata
    if re.search(r"\b(?:neurips|nips|neural information processing systems)\b", venue, re.I):
        return f"https://{NEURIPS}/paper_files/paper/{year}", name
    if re.search(r"\b(?:PMLR|Proceedings of Machine Learning Research)\b", venue, re.I):
        volume = re.search(r"\bvol(?:ume)?\.?\s+(\d{1,4})\b", venue, re.I)
        if volume:
            return f"https://{PMLR}/v{volume[1]}/", name
    conference = re.search(r"\b(?:EACL|NAACL|EMNLP|COLING|AACL|ACL)\b", venue, re.I)
    if conference or re.search(r"Association for Computational Linguistics", venue, re.I):
        # Old workshops are indexed together as WYY, including co-located workshops
        # whose printed bibliography gives ACL as publisher but omits the host event.
        if 1960 <= int(year) <= 2019 and re.search(r"\bWorkshop\b", venue, re.I):
            return ACL_COLLECTIONS + f"W{year[-2:]}.xml", name
    if conference:
        return f"https://{ACL}/events/{conference[0].lower()}-{year}/", name
    return None


class _VolumeIndex(HTMLParser):
    """Read the title, author list and paper URL from individual proceedings rows."""

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.host = urlsplit(url).hostname
        self.rows = defaultdict(list)
        self.row_tag = None
        self.row_depth = 0
        self.collect = None

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        classes = (attr.get("class") or "").split()
        if not self.row_tag:
            row = ((self.host == NEURIPS and tag == "li")
                   or (self.host == PMLR and tag == "div" and "paper" in classes)
                   or (self.host == ACL and tag == "div" and "d-sm-flex" in classes and "align-items-stretch" in classes))
            if not row:
                return
            self.row_tag, self.row_depth = tag, 1
            self.title, self.authors, self.href = [], [], ""
            return
        if tag == self.row_tag:
            self.row_depth += 1
        if self.collect:
            return
        href = attr.get("href") or ""
        if tag == "a" and href:
            link = urlsplit(urljoin(self.url, href))
            if (link.scheme not in {"http", "https"} or link.netloc != self.host or link.query or link.fragment):
                return
            path = link.path
            if self.host == NEURIPS and re.fullmatch(r"/(?:paper|paper_files/paper)/\d{4}/hash/[a-f0-9]+-Abstract(?:-[\w-]+)?\.html", path, re.I):
                self.href, self.collect = f"https://{self.host}{path}", (tag, self.title)
            elif (self.host == PMLR and path.startswith(urlsplit(self.url).path)
                  and re.fullmatch(r"/v\d{1,4}/[\w-]+\.html", path)):
                self.href = f"https://{self.host}{path}"
            elif self.host == ACL:
                if re.fullmatch(r"/(?:[A-Z]\d{2}-\d{4,5}|\d{4}\.[\w.-]+)/", path):
                    self.href, self.collect = f"https://{self.host}{path}", (tag, self.title)
                elif path.startswith("/people/"):
                    self.authors.append(",")
                    self.collect = (tag, self.authors)
        elif self.host == PMLR and tag == "p" and "title" in classes:
            self.collect = (tag, self.title)
        elif tag == "span" and ("authors" in classes or "paper-authors" in classes):
            self.collect = (tag, self.authors)
        elif self.host == NEURIPS and tag == "i" and self.href:
            self.collect = (tag, self.authors)

    def handle_data(self, data):
        if self.collect:
            self.collect[1].append(data)

    def handle_endtag(self, tag):
        if self.collect and tag == self.collect[0]:
            self.collect = None
        if tag != self.row_tag:
            return
        self.row_depth -= 1
        if self.row_depth == 0:
            first = "".join(self.authors).lstrip(",").split(",")[0]
            if self.href and self.title and first.strip():
                self.rows[title_identity_key("".join(self.title))].append((normalize_title(first).split(), self.href))
            self.row_tag = self.collect = None


def _lookup(rows, ref, author):
    matches = set()
    for full_name, url in rows.get(title_identity_key(ref["title"]), []):
        if first_author_agrees(author, full_name):
            matches.add(url)
    return matches


def _read_index(url, raw):
    if url.startswith(ACL_COLLECTIONS):
        collection = url.rsplit("/", 1)[1].removesuffix(".xml")
        root = ElementTree.fromstring(raw, parser=ElementTree.XMLParser(target=ElementTree.TreeBuilder(insert_comments=True)))
        rows = defaultdict(list)
        if root.tag == "collection" and root.get("id") == collection:
            for paper in root.findall("./volume/paper"):
                title = paper.find("title")
                author = paper.find("author")
                if title is None or author is None:
                    continue
                # Read the Anthology's published record URL; historical ID widths vary.
                urls = {child.text.strip() for child in paper if child.tag is ElementTree.Comment and child.text
                        and re.fullmatch(rf"https://aclanthology\.org/{re.escape(collection)}-\d+/", child.text.strip())}
                if len(urls) == 1:
                    full_name = " ".join(author.findtext(key, "") for key in ("first", "last"))
                    rows[title_identity_key("".join(title.itertext()))].append((normalize_title(full_name).split(), urls.pop()))
        return rows
    index = _VolumeIndex(url)
    index.feed(raw.decode("utf-8"))
    index.close()
    return index.rows


def resolve_proceedings_links(catalogue, *, max_seconds=15):
    """Look up each cited volume once per pass, leaving unmatched references intact."""
    deadline = time.monotonic() + max_seconds
    groups = defaultdict(list)
    for ref in catalogue.values():
        if ref.get("link_kind") != "arxiv_search":
            continue
        location = _index_for(ref)
        checks = ref.setdefault("link_checks", {})
        if location:
            url, author = location
            checks.setdefault("proceedings", "not_attempted")
            groups[url].append((ref, author))
        else:
            checks["proceedings"] = "insufficient_metadata"
    def last_checked(group):
        return min(ref.get("link_checked_at", {}).get("proceedings", 0) for ref, _ in group[1])

    for url, refs in sorted(groups.items(), key=last_checked):
        host = urlsplit(url).hostname
        now = time.monotonic()
        if deadline - now < 0.75:
            break
        if _pause_until.get(host, 0) > now:
            continue
        rows = {}
        status = "unavailable"
        try:
            request = Request(url, headers={"User-Agent": "KESearch-SurveyReader/1.0"})
            raw = fetch_bounded(request, timeout=min(5, deadline - now), limit=16 * 1024 * 1024)
            rows = _read_index(url, raw)
            if rows:
                status = "not_found"
        except HTTPError as error:
            if error.code == 429:
                status = "rate_limited"
                retry_after = error.headers.get("Retry-After", "") if error.headers else ""
                _pause_until[host] = time.monotonic() + (int(retry_after) if re.fullmatch(r"\d{1,7}", retry_after) else 60)
        except (OSError, URLError, HTTPException, ValueError, ElementTree.ParseError):
            pass
        for ref, author in refs:
            result = status
            if status == "not_found":
                urls = _lookup(rows, ref, author)
                if len(urls) == 1:
                    ref.update(link_kind="source", url=urls.pop())
                    result = "matched"
                elif urls:
                    result = "ambiguous"
            ref["link_checks"]["proceedings"] = result
            ref.setdefault("link_checked_at", {})["proceedings"] = time.time()
