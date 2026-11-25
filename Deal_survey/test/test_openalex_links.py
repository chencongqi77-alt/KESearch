import json
import unittest
from unittest.mock import patch

from deal_survey import openalex_links as links


class OpenAlexLinksTests(unittest.TestCase):
    def setUp(self):
        self.ref = {"title": "Research in C++", "entry": '[9] R. Author, "Research in C++," Conference, 2010, pp. 53–58.',
                    "link_kind": "arxiv_search", "url": "https://arxiv.org/search/"}
        self.paper = {"id": "https://openalex.org/W12", "title": "Research in C++", "publication_year": 2010,
                      "authorships": [{"author": {"display_name": "René Author"}}], "biblio": {"first_page": "53"},
                      "primary_location": {"landing_page_url": "http://www.wseas.us/e-library/conferences/2010/example.pdf"}}

    def run_lookup(self, works, total=None):
        payload = {"meta": {"count": len(works) if total is None else total}, "results": works}
        with (patch.object(links, "_next_request", 0),
              patch.object(links, "fetch_bounded", return_value=json.dumps(payload).encode())):
            links.resolve_openalex_links({"ref": self.ref})
        return self.ref["link_checks"]["openalex"]

    def test_returns_publisher_full_text_and_index_record(self):
        self.assertEqual(self.run_lookup([self.paper]), "matched")
        self.assertEqual(self.ref["url"], "https://www.wseas.us/e-library/conferences/2010/example.pdf")
        self.assertEqual(self.ref["link_record"], self.paper["id"])

    def test_rejects_conflicting_metadata_generic_landing_page_and_lookalike_hosts(self):
        for changes in ({"title": "Research in C#"}, {"publication_year": 2011}, {"biblio": {"first_page": "8"}},
                        {"authorships": [{"author": {"display_name": "Ben Author"}}]},
                        {"primary_location": {"landing_page_url": "https://www.wseas.us/"}},
                        {"primary_location": {"pdf_url": "https://wseas.us.example.com/e-library/f.pdf"}}):
            with self.subTest(changes=changes):
                self.assertEqual(self.run_lookup([{**self.paper, **changes}]), "not_found")
                self.assertEqual(self.ref["link_kind"], "arxiv_search")

    def test_keeps_search_when_ambiguous_or_result_set_truncated(self):
        self.assertEqual(self.run_lookup([self.paper, {**self.paper, "id": "https://openalex.org/W2"}]), "ambiguous")
        self.assertEqual(self.run_lookup([self.paper], total=20), "incomplete")
