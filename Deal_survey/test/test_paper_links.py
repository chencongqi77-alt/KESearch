import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from deal_survey import paper_links


TITLE = "Análisis of Paper Retrieval"


def reference(kind="arxiv_search"):
    return {"link_kind": kind, "title": TITLE, "entry": f"[1] A. García, “{TITLE},” vol. 7, 2010.", "url": "original"}


def record(doi="10.1234/example", title="ANALISIS OF PAPER RETRIEVAL", author="Garcia", year=2010):
    return {"title": [title], "author": [{"family": author}], "issued": {"date-parts": [[year]]}, "DOI": doi}


def response(*rows):
    return json.dumps({"status": "ok", "message": {"items": list(rows)}}).encode()


def journal_reference():
    return {**reference(), "entry": f"[1] A. García, “{TITLE},” Example Journal, vol. 8, no. 3, pp. 229–256, 2010."}


def journal_record(doi):
    return {**record(doi), "type": "journal-article", "container-title": ["Example Journal"], "volume": "8",
            "issue": "3-4", "page": "229-256", "author": [{"given": "Ada", "family": "García"}],
            "ISSN": ["1234-567X"], "publisher": "Example Publisher"}


class PublicationLinkTests(unittest.TestCase):
    def setUp(self):
        timer = patch.object(paper_links, "_next_query", 0.0)
        timer.start()
        self.addCleanup(timer.stop)

    def test_only_search_links_with_a_printed_title_and_author_are_queried(self):
        ref = reference()
        catalogue = {"lookup": ref, "a": reference("arxiv"), "b": reference("doi"), "c": reference("source"),
                     "unparsed": {**reference(), "title": reference()["entry"]},
                     "unknown_author": {**reference(), "entry": f"[4] {TITLE}. García, 2010."}}
        with patch.object(paper_links, "fetch_bounded", return_value=response(
                record(author="Wrong"), record(), record(doi="10.1234/EXAMPLE"))) as fetch:
            paper_links.resolve_publication_links(catalogue)
        self.assertEqual(ref["url"], "https://doi.org/10.1234/example")
        self.assertTrue(all(item["url"] == "original" for key, item in catalogue.items() if key != "lookup"))
        request, = fetch.call_args.args
        url = urlsplit(request.full_url)
        self.assertEqual((url.scheme, url.netloc, url.path), ("https", "api.crossref.org", "/works"))
        self.assertIn(TITLE, parse_qs(url.query)["query.bibliographic"][0])
        fetch.assert_called_once()

    def test_rejects_ambiguous_approximate_or_contradictory_candidates(self):
        title, authors, years = paper_links._citation(reference())
        for rows in ([record(), record(doi="10.5678/other")], [record(title="Paper Retrieval")],
                     [record(author="Wrong")], [record(year=2012)], [record(doi="https://wrong.example")],
                     [{**record(), "subtitle": ["Another volume"]}], [None, {"title": None}]):
            with self.subTest(rows=rows):
                self.assertFalse(paper_links._match_records(rows, title, authors, years,
                                                            paper_links._publication(reference()))[2])

    def test_separate_book_chapter_from_two_confirmed_journal_locations(self):
        ref = journal_reference()
        first, second = journal_record("10.1234/article"), journal_record("10.1234/other")
        chapter = {**first, "DOI": "10.5678/chapter", "type": "book-chapter",
                   "container-title": ["Another Book"], "page": "5-32"}
        with patch.object(paper_links, "fetch_bounded", return_value=response(chapter, second, first)):
            paper_links.resolve_publication_links({"work": ref})
        self.assertEqual(ref["link_evidence"], "crossref_journal_location")
        self.assertEqual(ref["url"], "https://doi.org/10.1234/article")
        self.assertEqual(ref["alternate_urls"], ["https://doi.org/10.1234/other"])
        self.assertEqual(ref["link_checks"]["crossref"], "matched")
        title, authors, years = paper_links._citation(journal_reference())
        location = paper_links._publication(journal_reference())
        for wrong in [chapter, {**first, "volume": "9"}, {**first, "issue": "5"}, {**first, "page": "229-255"},
                      {**first, "container-title": ["Example Journal Supplement"]}]:
            self.assertEqual(paper_links._match_records([wrong], title, authors, years, location)[0], "not_found")

    def test_ocr_word_boundaries_match_only_the_full_title_and_first_author(self):
        ref = {**reference(), "title": "Crosslevel attentionbased analysis for C++",
               "entry": "[1] A. García and B. Smith, “Crosslevel attentionbased analysis for C++,” 2010."}
        candidate = "Cross-Level Attention-Based Analysis for C++"
        args = (*paper_links._citation(ref), paper_links._publication(ref))
        self.assertEqual(paper_links._match_records([record(title=candidate)], *args)[0], "matched")
        for row in [record(title=candidate.replace("C++", "C#")), record(title=candidate.replace("C++", "C")),
                    record(title=candidate.replace("Analysis", "Analyses")), record(title=candidate, author="Smith"),
                    record(title=candidate, year=2016), {**record(title=candidate), "issued": None}]:
            self.assertEqual(paper_links._match_records([row], *args)[0], "not_found")

    def test_same_journal_entries_need_full_authors_issn_publisher_and_page_range(self):
        ref = journal_reference()
        first, second = journal_record("10.1234/first"), journal_record("10.1234/second")
        citation = paper_links._citation(ref)
        location = paper_links._publication(ref)
        for other in [{**second, "author": [{"given": "Alice", "family": "Garcia"}]},
                      {**second, "author": [*second["author"], {"given": "B", "family": "Smith"}]},
                      {**second, "ISSN": ["1111-1111"]}, {**second, "publisher": "Different Press"},
                      {**second, "page": "229"}, {**second, "issued": {}}]:
            self.assertEqual(paper_links._match_records([first, other], *citation, location)[0], "ambiguous")
        short = {**ref, "entry": ref["entry"].replace("229–256", "229")}
        self.assertEqual(paper_links._match_records([first, second], *citation, paper_links._publication(short))[0],
                         "ambiguous")

    def test_explicit_identical_relation_and_other_relations_are_distinguished(self):
        ref = reference()
        first, second = record("10.1234/first"), record("10.1234/second")
        related = [{"id": "https://doi.org/10.1234/first", "id-type": "doi"}]
        for key, expected in [("is-part-of", "ambiguous"), ("is-identical-to", "matched")]:
            second["relation"] = {key: related}
            state, evidence, urls = paper_links._match_records(
                [first, second], *paper_links._citation(ref), paper_links._publication(ref))
            self.assertEqual(state, expected)
            if state == "matched":
                self.assertEqual((evidence, len(urls)), ("crossref_identical_relation", 2))

    def test_retry_budget_prioritizes_unvisited_refs_without_forgetting_known_misses(self):
        known = {**reference(), "link_checks": {"crossref": "not_found"}, "link_checked_at": {"crossref": 1}}
        new = reference()
        with patch.object(paper_links, "fetch_bounded", side_effect=TimeoutError()):
            paper_links.resolve_publication_links({"a": known, "b": new})
        self.assertEqual(new["link_checks"]["crossref"], "unavailable")
        self.assertGreater(new["link_checked_at"]["crossref"], 1)
        self.assertEqual(known["link_checks"]["crossref"], "not_found")

    def test_rate_limit_stops_this_run_and_the_next_short_budget(self):
        ref = reference()
        error = HTTPError("https://api.crossref.org/works", 429, "", {"Retry-After": "90"}, None)
        with patch.object(paper_links, "fetch_bounded", side_effect=error) as fetch:
            paper_links.resolve_publication_links({"a": ref, "b": reference()})
            paper_links.resolve_publication_links({"a": ref}, max_seconds=5)
            fetch.assert_called_once()
        self.assertEqual(ref["link_kind"], "arxiv_search")

    def test_an_unavailable_service_or_expired_budget_preserves_links(self):
        ref = reference()
        with patch.object(paper_links, "fetch_bounded", side_effect=TimeoutError()) as fetch:
            paper_links.resolve_publication_links({"a": ref}, max_seconds=0)
            fetch.assert_not_called()
            paper_links.resolve_publication_links({"a": ref, "b": reference()})
            fetch.assert_called_once()
        self.assertEqual(ref["url"], "original")


if __name__ == "__main__":
    unittest.main()
