import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deal_survey import pdf_check


def mention(marker, *numbers):
    return {"marker": marker, "targets": [{"number": number} for number in numbers]}


class CountComparisonTests(unittest.TestCase):
    def test_compare_visible_group_labels_and_keep_page_numbers_separate(self):
        references = [{"number": n} for n in range(1, 6)]
        mentions = [mention("[2, 3–5]", 2, 3, 4, 5), mention("[2]", 2), mention("(Smith, 2024)")]
        pdf_counts = {1: {1: 1}, 2: {1: 1, 3: 1}, 3: {3: 1}, 4: {}, 5: {3: 1}}
        with patch.object(pdf_check, "_read_pdf_links", return_value=(pdf_counts, {})):
            result = pdf_check.check_pdf_citations("sample.pdf", references, mentions)
        self.assertEqual(result["status"], "differences")
        self.assertEqual(result["differences"], [{"label": 1, "pdf_count": 1, "parsed_count": 0,
                                                  "pdf_pages": [1], "pdf_excerpts": []}])
        self.assertEqual(result["parsed_count"], 4)

    def test_optional_dependency_and_duplicate_reference_numbers(self):
        with patch.object(pdf_check, "_read_pdf_links", side_effect=ImportError):
            result = pdf_check.check_pdf_citations("sample.pdf", [], [])
            self.assertEqual(result["reason"], "pymupdf_unavailable")
        with patch.object(pdf_check, "_read_pdf_links", return_value=({1: {1: 1}}, {})):
            result = pdf_check.check_pdf_citations("sample.pdf", [{"number": 1}] * 2, [mention("[1]", 1)])
            self.assertEqual(result["status"], "unverified")
            self.assertEqual(result["reason"], "ambiguous_parsed_bibliography_numbers")


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "Optional PyMuPDF PDF checks")
class PdfLinkTests(unittest.TestCase):
    def make_pdf(self, path, body_number=1, link=True):
        import pymupdf

        with pymupdf.open() as pdf:
            for _ in range(2):
                pdf.new_page(width=300, height=400)
            body = pdf[0]
            label = f"[{body_number}]"
            body.insert_text((50, 100), "See " + label + ".")
            bibliography = pdf[1]
            bibliography.insert_text((50, 100), "[1] Some paper.")
            if link:
                body.insert_link({"kind": pymupdf.LINK_GOTO, "from": body.search_for(label)[0],
                                  "page": 1, "to": pymupdf.Point(50, 100)})
                link_xref = pdf[0].annot_xrefs()[0][0]
                pdf.xref_set_key(link_xref, "A/D", "(cite.paper)")
                x, y = bibliography.get_text("words")[0][:2]
                # Named destinations use PDF coordinates with origin at bottom left.
                names = f"<</Dests<</Names[(cite.paper)[{bibliography.xref} 0 R /XYZ {x} {400-y+1} 0]]>>>>"
                pdf.xref_set_key(pdf.pdf_catalog(), "Names", names)
            pdf.save(path)

    def test_original_pdf_geometry_detects_missing_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "survey.pdf"
            self.make_pdf(path)
            result = pdf_check.check_pdf_citations(path, [{"number": 1}], [])
            difference, = result["differences"]
            self.assertEqual([difference[k] for k in ("label", "pdf_count", "parsed_count", "pdf_pages")], [1, 1, 0, [1]])
            sample, = difference["pdf_excerpts"]
            self.assertEqual(sample["quote"], "See [1].")
            self.assertEqual(sample["page"], 1)
            self.assertGreater(sample["rect"][0], sample["quote_rect"][0])
            self.assertNotIn("section_id", sample)
            result = pdf_check.check_pdf_citations(path, [{"number": 1}], [mention("[1]", 1)])
            self.assertEqual(result["status"], "matched")

    def test_ambiguous_line_has_no_excerpt(self):
        import pymupdf

        box = pymupdf.Rect(0, 0, 90, 10)
        center = pymupdf.Point(6, 5)
        callout = (3, center, [("A [3] quotation.", box)], 0)
        self.assertIsNone(pdf_check._excerpt(callout, [box, box], 1, box, pymupdf))

    def test_wrong_printed_label_and_unlinked_pdf_are_unverified(self):
        for printed, link, reason in [(2, True, "body_label_and_destination_unconfirmed"),
                                      (1, False, "no_named_citation_destinations")]:
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "survey.pdf"
                self.make_pdf(path, body_number=printed, link=link)
                result = pdf_check.check_pdf_citations(path, [{"number": 1}], [mention("[1]", 1)])
                self.assertEqual(result["status"], "unverified")
                self.assertEqual(result["reason"], reason)


if __name__ == "__main__":
    unittest.main()
