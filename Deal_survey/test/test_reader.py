import base64
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree
from zipfile import ZipFile

from pypdf import PdfWriter

from deal_survey import reader
from deal_survey.prepare import build_pack


PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/"
                       "x8AAwMCAO+jx1sAAAAASUVORK5CYII=")


class ReaderTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)
        self.pdf = self.work / "sample.pdf"
        writer = PdfWriter()
        for _ in range(2):
            writer.add_blank_page(200, 200)
        writer.write(self.pdf)
        self.archive = self.work / "mineru.zip"
        self.assets = self.work / "assets"
        body = [
            {"type": "title", "text": "Study of Systems"},
            {"type": "text", "text": "Abstract—We review measurements of systems."},
            {"type": "text", "text": "1 Methods", "text_level": 1},
            {"type": "text", "text": "We compare [1, 2] in two settings. Later [1] is given as a baseline."},
            {"type": "image", "img_path": "images/first.jpg", "image_caption": ["Figure 1. Overview [2]."]},
            {"type": "text", "text": "2 Results", "text_level": 1, "page_idx": 1},
            {"type": "text", "text": "Smith's measurement [2] is more stable.", "page_idx": 1},
            {"type": "table", "img_path": "../chart.png", "table_body": "<table><tr><td>Method [1]</td></tr></table>"},
            {"type": "image", "img_path": "images/active.svg", "image_caption": ["Figure 2. Missing original."]},
            {"type": "equation", "text": "$$ x = 2 $$"},
            {"type": "text", "text": "References", "text_level": 1},
            {"type": "list", "sub_type": "ref_text", "list_items": [
                '[1] A. Smith, “Methods for data,” arXiv:2202.12345v2; doi:10.5555/abc, 2022.',
                '[2] J. Li. A second work. In an Annual Meeting, 2022. https://doi.org/10.5555/paper(8).',
                '[3] B. Young, “Unused work,” 2015.']},
        ]
        for block in body:
            block.setdefault("page_idx", 0)
        with ZipFile(self.archive, "w") as z:
            z.writestr("parse/paper_origin.pdf", self.pdf.read_bytes())
            z.writestr("parse/paper_content_list.json", json.dumps(body))
            z.writestr("parse/full.md", "# Study\n")
            z.writestr("parse/images/first.jpg", PNG)
            z.writestr("parse/images/active.svg", b"<svg></svg>")
            z.writestr("chart.png", PNG)
        self.pack = build_pack(self.pdf, self.archive)

    def document(self):
        return reader.build_reader(self.pack, self.archive, self.assets, asset_url_prefix="/assets/",
                                   summarize=False)

    def test_offline_reading_preserves_source_and_specific_discussion(self):
        with patch.object(reader, "_fetch", side_effect=AssertionError):
            doc = self.document()
        self.assertEqual((doc["pages"], doc["figure_count"], doc["reference_count"]), (2, 1, 3))
        self.assertEqual(doc["summary"], {"source": "abstract", "text": "We review measurements of systems.",
                                          "warning": None})
        _, methods, results, bibliography = doc["sections"]
        first, second = methods["references"]
        self.assertEqual(first["url"], "https://arxiv.org/abs/2202.12345v2")
        self.assertEqual(second["url"], "https://doi.org/10.5555/paper(8)")
        self.assertEqual(second["title"], "A second work")
        self.assertEqual([q["text"] for q in first["quotes"]],
                         ["We compare [1, 2] in two settings.", "Later [1] is given as a baseline."])
        self.assertIn("Overview", second["quotes"][1]["text"])
        self.assertEqual(results["references"][0]["quotes"][0]["page"], 2)
        self.assertEqual(results["references"][1]["quotes"][0]["text"], "Method [1]")
        self.assertEqual(results["blocks"][-1]["kind"], "equation")
        self.assertEqual(bibliography["references"], [])
        self.assertEqual([b["bibliography_ids"] for b in bibliography["blocks"]],
                         [["ref-0001"], ["ref-0002"], ["ref-0003"]])
        self.assertEqual(doc["references"][-1]["link_kind"], "arxiv_search")
        image_name = sha256(PNG).hexdigest() + ".png"
        self.assertEqual(methods["blocks"][-1]["src"], "/assets/" + image_name)
        self.assertEqual([p.name for p in self.assets.iterdir()], [image_name])
        self.assertEqual((self.assets / image_name).read_bytes(), PNG)

    def test_mixed_archive_rejected_before_publishing_assets(self):
        self.archive.write_bytes(self.archive.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "指纹"):
            self.document()
        self.assertEqual(list(self.assets.glob("*")), [])

    def test_original_pdf_excerpts_only_join_a_unique_same_page_prose_boundary(self):
        shared = "A long discussion shared between two possible sections."
        unique = "Uniquely worded beginning of a parsed paragraph"
        only_inside = "Some material is in the middle of a longer paragraph"
        def evidence(label, overlap):
            return {"label": label, "pdf_excerpts": [{"page": 1, "rect": [5, 6, 8, 9],
                    "quote_rect": [2, 3, 10, 11], "quote": f"Review discussion [{label}].\n{overlap}"}]}

        def paragraph(text, index, page=1):
            return {"text": text, "kind": "text", "page": page, "block_index": index}

        catalogue = {str(n): {"number": n, "id": str(n)} for n in (1, 2, 3, 4)}
        sections = [{"id": "A", "blocks": [paragraph(shared, 2), paragraph(unique + " continues here.", 3),
                                          paragraph("Before. " + only_inside + ". After.", 4)], "references": []},
                    {"id": "B", "blocks": [paragraph(shared, 7), paragraph(unique, 8, page=2)], "references": []}]
        differences = [evidence(1, unique), evidence(2, shared), evidence(3, only_inside),
                       evidence(4, "An entirely missing quotation.")]
        pack = {"pdf_check": {"status": "differences", "differences": differences}}
        reader._pdf_evidence(sections, pack, catalogue)
        self.assertEqual([r["id"] for r in sections[0]["references"]], ["1"])
        self.assertEqual(sections[1]["references"], [])
        quote, = sections[0]["references"][0]["quotes"]
        self.assertEqual((quote["source"], quote["page"], quote["text"]), ("pdf", 1, differences[0]["pdf_excerpts"][0]["quote"]))
        self.assertNotIn("block_index", quote)
        self.assertTrue(all(r.get("pdf_excerpts") for r in catalogue.values()))
        self.assertEqual(catalogue["2"]["pdf_excerpts"][0]["rect"], [5, 6, 8, 9])

    def test_paper_links_require_a_recognizable_identifier_or_source(self):
        link = reader._reference_link
        self.assertEqual(link("CoRR abs/hep-th/9901001v2.", None)[1], "https://arxiv.org/abs/hep-th/9901001v2")
        self.assertEqual(link("Paper. doi:10.48550/arXiv.2301.10101.", None)[0], "arxiv")
        self.assertEqual(link("Paper. https://aclanthology.org/2023.acl-long.1/", "Paper")[0], "source")
        self.assertEqual(link("Paper. https://aclanthology.org@elsewhere.invalid/a", None)[0], "arxiv_search")
        self.assertEqual(link("Paper. https://github.com/example/experiments", None)[0], "arxiv_search")
        self.assertIn("searchtype=all", link("Unknown authorship", None)[1])

    def test_optional_math_preserves_tex_and_only_emits_presentation_elements(self):
        outline = [{"blocks": [{"kind": "text", "text": r"$\alpha_i$ and $$\frac{1}{2}$$ and `$z$`"},
                               {"kind": "text", "text": r"$\href{https://test.invalid}{x}$"}],
                    "references": []}]
        with patch.dict(sys.modules, {"latex2mathml.converter": None}):
            self.assertEqual(reader.formula_dictionary(outline), {})
        try:
            import latex2mathml.converter
        except ImportError:
            self.skipTest("可选 MathML 转换库未安装")
        math = reader.formula_dictionary(outline)
        self.assertEqual(set(math), {r"$\alpha_i$", r"$$\frac{1}{2}$$"})
        namespace = "{http://www.w3.org/1998/Math/MathML}"
        alpha = ElementTree.fromstring(math[r"$\alpha_i$"])
        self.assertEqual(alpha.tag, namespace + "math")
        self.assertEqual(alpha.get("display"), "inline")
        self.assertIn("α", "".join(alpha.itertext()))
        fraction = ElementTree.fromstring(math[r"$$\frac{1}{2}$$"])
        self.assertEqual(fraction.get("display"), "block")
        self.assertIsNotNone(fraction.find(".//" + namespace + "mfrac"))
        self.assertIn(r"$\alpha_i$", outline[0]["blocks"][0]["text"])

    def test_arxiv_requires_unique_title_and_bibliography_author_match(self):
        def atom(identity, title, name):
            return (f"<entry><id>http://arxiv.org/abs/{identity}</id><title>{title}</title>"
                    f"<author><name>{name}</name></author></entry>")

        feed = ('<feed xmlns="http://www.w3.org/2005/Atom">'
                + atom("2010.00321v1", "Testing a model", "Ben Smith")
                + atom("2010.12346", "Another paper", "Wrong Person")
                + atom("2010.12347", "Conflicting titles", "Ben Young")
                + atom("2010.12348", "Conflicting titles", "Beth Young") + "</feed>").encode()
        refs = [{"title": title, "entry": f'B. {name}, “{title},” 2020.', "link_kind": "arxiv_search"}
                for title, name in [("Testing a Model", "Smith"), ("Another paper", "Doe"),
                                    ("Conflicting titles", "Young")]]
        with patch.object(reader, "_fetch", return_value=feed):
            reader._title_batch(refs, 1)
        self.assertEqual(refs[0]["url"], "https://arxiv.org/abs/2010.00321v1")
        self.assertEqual([ref["link_kind"] for ref in refs[1:]], ["arxiv_search"] * 2)
        self.assertEqual([ref["link_checks"]["arxiv"] for ref in refs], ["matched", "not_found", "ambiguous"])

    def test_arxiv_retrieves_merged_ocr_but_requires_full_title_and_first_author(self):
        title = "Hierarchical questionimage co-attention for visual question answering"
        ref = {"title": title, "entry": f'[32] J. Lu and D. Parikh, “{title},” 2016.', "link_kind": "arxiv_search"}
        def entry(identity, candidate_title, authors):
            return (f"<entry><id>http://arxiv.org/abs/{identity}</id><title>{candidate_title}</title>"
                    + "".join(f"<author><name>{a}</name></author>" for a in authors) + "</entry>")
        corrected = title.replace("questionimage", "Question–Image")
        feed = ('<feed xmlns="http://www.w3.org/2005/Atom">'
                + entry("1606.00061v5", corrected, ["Jiasen Lu", "Devi Parikh"])
                + entry("1606.00555", corrected, ["Another Author", "Jiasen Lu"])
                + entry("1606.00556", corrected + " systems", ["Jiasen Lu"]) + "</feed>").encode()
        with patch.object(reader, "_fetch", return_value=feed) as fetch:
            reader._title_batch([ref], .5)
        query = parse_qs(urlsplit(fetch.call_args.args[0].full_url).query)["search_query"][0]
        self.assertIn('au:"lu"', query)
        self.assertTrue(any("questionimage" not in clause for clause in query.split(" OR ")))
        self.assertEqual(ref["url"], "https://arxiv.org/abs/1606.00061v5")
        self.assertEqual(ref["title"], title)
        self.assertEqual(ref["link_checks"]["arxiv"], "matched")

    def test_scientific_symbols_and_truncated_feeds_do_not_become_direct_links(self):
        title = "Evaluation of C# Models"
        base = {"title": title, "entry": f'B. Smith, “{title},” 2020.', "link_kind": "arxiv_search"}
        atom = ('<entry><id>http://arxiv.org/abs/2010.10000</id><title>{}</title>'
                '<author><name>Ben Smith</name></author></entry>')
        template = ('<feed xmlns="http://www.w3.org/2005/Atom" xmlns:op="http://a9.com/-/spec/opensearch/1.1/">'
                    '<op:totalResults>{}</op:totalResults>{}</feed>')
        for found, count, expected in [("Evaluation of C++ Models", 1, "not_found"), (title, 20, "incomplete")]:
            ref = deepcopy(base)
            feed = template.format(count, atom.format(found)).encode()
            with patch.object(reader, "_fetch", return_value=feed):
                reader._title_batch([ref], 1)
            self.assertEqual(ref["link_checks"]["arxiv"], expected)
            self.assertEqual(ref["link_kind"], "arxiv_search")

    def test_rate_limited_batch_does_not_mark_unattempted_entries_as_missing(self):
        catalogue = {str(i): {"entry": f"A. Smith. Example title {i}.", "title": f"Example title {i}",
                              "link_kind": "arxiv_search"} for i in range(8)}
        failure = HTTPError("https://export.arxiv.org/api/query", 429, "limited", {"Retry-After": "20"}, None)
        with patch.object(reader, "_next_arxiv_request", 0), patch.object(reader, "_fetch", side_effect=failure) as fetch:
            reader._resolve_titles(catalogue, max_seconds=5)
            reader._resolve_titles(catalogue, max_seconds=1)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual([r["link_checks"]["arxiv"] for r in catalogue.values()],
                         ["rate_limited"] * 6 + ["not_attempted"] * 2)
        self.assertNotIn("link_checked_at", catalogue["7"])

    def test_recheck_synchronizes_only_link_fields_across_all_section_copies(self):
        doc = self.document()
        first, second, last = doc["references"]
        last.update(link_kind="arxiv_search", link_checked_at={"arxiv": 4})
        second.update(link_kind="arxiv_search", url="https://arxiv.org/search/?query=sample")
        before = deepcopy(doc)
        visited = []
        def resolve(pending, **options):
            visited.extend(pending)
            record = next(iter(pending.values()))
            record.update(link_kind="arxiv", url="https://arxiv.org/abs/2201.10100",
                          link_evidence="arxiv_title_first_author")
            record["link_checks"]["arxiv"] = "matched"
        def miss(pending, **options):
            for ref in pending.values():
                ref["link_checks"]["crossref"] = "not_found"
        with (patch.object(reader, "_resolve_titles", side_effect=resolve),
              patch.object(reader, "resolve_proceedings_links"),
              patch.object(reader, "resolve_openalex_links"),
              patch.object(reader, "resolve_publication_links", side_effect=miss)):
            stats = reader.refresh_reference_links(doc)
        self.assertEqual(visited, [second["id"], last["id"]])
        self.assertEqual((stats["resolved"], stats["remaining"], stats["status"]), (1, 1, "partial"))
        self.assertEqual(first, before["references"][0])
        self.assertEqual(doc["summary"], before["summary"])
        for current, prior in zip(doc["sections"], before["sections"]):
            self.assertEqual(current["blocks"], prior["blocks"])
            for ref, original in zip(current["references"], prior["references"]):
                self.assertEqual(ref["quotes"], original["quotes"])
                if ref["id"] == second["id"]:
                    self.assertEqual(ref["link_checks"], {"arxiv": "matched"})
                    self.assertEqual(ref["url"], second["url"])

    def test_legacy_section_only_reader_uses_original_evidence_and_shared_fallback_budget(self):
        doc = self.document()
        doc.pop("references")
        catalog = reader.reference_catalogue(doc)
        target = catalog["ref-0001"]
        for section in doc["sections"]:
            for ref in section["references"]:
                if ref["id"] == target["id"]:
                    ref.update(link_kind="arxiv_search", url="https://arxiv.org/search/?query=sample")
        before = deepcopy(doc)
        budgets = {}
        def crossref(items, *, max_seconds):
            budgets["crossref"] = max_seconds
            items[target["id"]]["link_checks"]["crossref"] = "not_found"
        def openalex(items, *, max_seconds):
            budgets["openalex"] = max_seconds
            items[target["id"]].update(link_kind="source", url="https://publisher.example/paper",
                                        link_record="https://openalex.org/W123456789")
            items[target["id"]]["link_checks"]["openalex"] = "matched"
        with (patch.object(reader, "_resolve_titles"), patch.object(reader, "resolve_proceedings_links"),
              patch.object(reader, "resolve_publication_links", side_effect=crossref),
              patch.object(reader, "resolve_openalex_links", side_effect=openalex)):
            stats = reader.refresh_reference_links(doc, max_seconds=70)
        self.assertLessEqual(budgets["crossref"], 62)
        self.assertGreaterEqual(budgets["openalex"], 8)
        self.assertEqual((stats["resolved"], stats["remaining"], stats["status"]), (1, 0, "complete"))
        self.assertNotIn("references", doc)
        for current, old in zip(doc["sections"], before["sections"]):
            for ref, previous in zip(current["references"], old["references"]):
                self.assertEqual(ref["quotes"], previous["quotes"])
                if ref["id"] == target["id"]:
                    self.assertTrue(ref["link_record"].startswith("https://openalex.org/"))

    def test_summary_and_redacted_fallback_keep_the_document_readable(self):
        document = self.document()
        env = {"DEEPSEEK_API_KEY": "for-test-only", "KET_CHAT_MODEL": "deepseek-reader-model"}
        response = b'{"choices":[{"finish_reason":"stop","message":{"content":" Summary "}}]}'
        with patch.dict(os.environ, env, clear=True), patch.object(reader, "_fetch", return_value=response) as fetch:
            self.assertEqual(reader.summarize_reader(document),
                             {"text": "Summary", "source": "deepseek", "warning": None})
        request = fetch.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.deepseek.com/chat/completions")
        prompt = json.loads(request.data)
        self.assertEqual(prompt["model"], "deepseek-reader-model")
        self.assertIn("2 Results", prompt["messages"][1]["content"])
        self.assertNotIn("Unused work", prompt["messages"][1]["content"])
        with patch.dict(os.environ, env, clear=True), patch.object(
                reader, "_fetch", side_effect=HTTPError(request.full_url, 402, "for-test-only", {}, None)):
            fallback = reader.summarize_reader(document)
        self.assertEqual(fallback["text"], document["summary"]["text"])
        self.assertIn("余额", fallback["warning"])
        self.assertNotIn("for-test-only", str(fallback))
        for bad_env in ({}, {**env, "KET_DEEPSEEK_BASE_URL": "https://example.invalid/"}):
            with patch.dict(os.environ, bad_env, clear=True), patch.object(reader, "_fetch", side_effect=AssertionError):
                self.assertTrue(reader.summarize_reader(document)["warning"])


if __name__ == "__main__":
    unittest.main()
