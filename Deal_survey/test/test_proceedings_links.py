import unittest
from unittest.mock import patch

from deal_survey import proceedings_links as links


def reference(title, venue, author="A. Reader"):
    return {"entry": f'[8] {author}, “{title},” {venue}.', "title": title,
            "link_kind": "arxiv_search", "url": "https://arxiv.org/search/"}


class ProceedingsTests(unittest.TestCase):
    def test_reads_volume_once_checks_author_and_never_uses_foreign_url(self):
        # The same book contains distinct papers; an author mismatch must stay unresolved.
        refs = {key: reference(title, "PMLR, vol. 8, 2012") for key, title in
                (("a", "Multiagent retrieval"), ("b", "Shared name"), ("c", "C++ queries"))}
        row = ('<div class="paper"><p class="title">{title}</p><span class="authors">{author}</span>'
               '<p><a href="{url}">abs</a></p></div>')
        raw = "".join(row.format(title=title, author=author, url=url) for title, author, url in [
            ("Multi-agent retrieval", "Anna Reader, Lily Ever", "/v8/reader.html"),
            ("Shared name", "Bill Reader", "/v8/bill.html"),
            ("Shared name", "Anna Reader", "https://example.org/v8/reader.html"),
            ("C# queries", "Anna Reader", "/v8/csharp.html"),
        ])
        with patch.object(links, "fetch_bounded", return_value=raw.encode()) as fetch:
            links.resolve_proceedings_links(refs)
        fetch.assert_called_once()
        self.assertEqual(refs["a"]["url"], "https://proceedings.mlr.press/v8/reader.html")
        self.assertEqual([r["link_checks"]["proceedings"] for r in refs.values()], ["matched", "not_found", "not_found"])

    def test_neurips_and_acl_nested_titles_and_ambiguous_rows(self):
        acl = '<div class="d-sm-flex align-items-stretch"><div><a href="/P02-1040.pdf">pdf</a></div><span>' \
              '<a href="/P02-1040/"><span>B</span>leu</a><a href="/people/a/">Anna Reader</a></span></div>'
        acl_data = links._read_index("https://aclanthology.org/events/acl-2002/", acl.encode())
        self.assertEqual(acl_data["bleu"], [(["anna", "reader"], "https://aclanthology.org/P02-1040/")])
        neurips = '<li><a href="/paper_files/paper/2010/hash/ab-Abstract.html">A <em>paper</em></a>' \
                  '<span class="paper-authors">Anna Reader, Joe Smith</span></li>'
        ref = reference("A paper", "NIPS 2010")
        with patch.object(links, "fetch_bounded", return_value=(neurips + neurips.replace("ab-", "ce-")).encode()):
            links.resolve_proceedings_links({"a": ref})
        self.assertEqual(ref["link_checks"]["proceedings"], "ambiguous")
        self.assertEqual(ref["link_kind"], "arxiv_search")

    def test_historical_workshop_record_uses_published_edition_and_preserves_source_text(self):
        xml = ('<collection id="W18"><volume id="54"><paper id="29"><!-- https://aclanthology.org/W18-5429/ -->'
               '<title>Importance of <fixed-case>Self</fixed-case>-Attention</title>'
               '<author><first>André</first><last>Reader</last></author></paper></volume></collection>')
        ref = reference(r"Impor- \` tance of Selfattention", "Workshop (ACL 2018)")
        old_entry = ref["entry"]
        with patch.object(links, "fetch_bounded", return_value=xml.encode()):
            links.resolve_proceedings_links({"a": ref})
        self.assertEqual(ref["url"], "https://aclanthology.org/W18-5429/")
        self.assertEqual(ref["entry"], old_entry)

    def test_empty_index_is_unavailable_and_no_time_is_not_no_match(self):
        ref = reference("Some work", "NIPS 2010")
        with patch.object(links, "fetch_bounded", return_value=b"<html>service unavailable</html>") as fetch:
            links.resolve_proceedings_links({"a": ref}, max_seconds=0)
            self.assertEqual(ref["link_checks"]["proceedings"], "not_attempted")
            fetch.assert_not_called()
            links.resolve_proceedings_links({"a": ref})
        self.assertEqual(ref["link_checks"]["proceedings"], "unavailable")
