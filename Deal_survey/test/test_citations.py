"""Offline regression cases for bibliography and section-bound discussion evidence."""
import unittest

from deal_survey.citations import bibliography_indices, build_citations


def text(value, **kw):
    return {"type": "text", "text": value, "page_idx": 0, **kw}


def reference(value):
    return text(value, type="ref_text")


def body(blocks):
    return [{"text": b["text"], "field": "text", "block_index": i, "page": 1,
             "section_id": "s1"} for i, b in enumerate(blocks) if "text" in b]


class CitationTests(unittest.TestCase):
    def test_grouped_numbers_and_evidence_spans(self):
        blocks = [text("Opening. The surveys [1, 3–4] contrast the models. See also [1]–[3]."),
                  text("REFERENCES", text_level=1),
                  reference('[1] A. Smith, “First model,” 2019.'),
                  reference("[2] B. Zhao. 2020. More models."),
                  reference("[3] C. Hu. Models and"), reference("methods. 2021."),
                  reference("[4] D. Doe. 2022. Fourth model.")]
        result = build_citations(blocks, body(blocks))
        refs, mentions = result["references"], result["mentions"]
        self.assertEqual(len(refs), 4)
        self.assertEqual(refs[0]["title"], "First model")
        self.assertEqual(len(refs[2]["source_spans"]), 2)
        self.assertEqual([m["reference_ids"] for m in mentions], [
            [refs[i]["id"] for i in (0, 2, 3)], [refs[i]["id"] for i in (0, 1, 2)]])
        self.assertEqual(mentions[0]["context"], "The surveys [1, 3–4] contrast the models.")
        for mention in mentions:
            field = blocks[mention["block_index"]][mention["field"]]
            self.assertEqual(field[mention["start"]:mention["end"]], mention["marker"])
            self.assertEqual(field[mention["context_start"]:mention["context_end"]], mention["context"])

    def test_ambiguous_and_missing_numbers(self):
        blocks = [text("Previous work [1, 2, 3]."), reference("[1] First."),
                  reference("[2] Second."), reference("[2] Other.")]
        result = build_citations(blocks, body(blocks))
        mention, = result["mentions"]
        self.assertEqual(mention["reference_ids"], ["ref-0001"])
        self.assertEqual(mention["status"], "partial")
        self.assertEqual([t["status"] for t in mention["targets"]], ["matched", "ambiguous", "unresolved"])
        self.assertEqual(result["diagnostics"][0]["code"], "duplicate_reference_number")

    def test_author_year_discussion_and_ambiguous_surnames(self):
        blocks = [text("As Smith et al. (2020) report, results vary (Smith, 2020; Brown and Díaz, 2019a)."
                       " Elsewhere (Brown & Other, 2019a; Wang, 2019) the ranking changes."),
                  text("References", text_level=1),
                  reference("J. Smith and A. Doe. 2020. First baselines. Press."),
                  reference("X. Smith and B. Chen. 2020. New baselines. Press."),
                  reference("Brown, T. and Díaz, J. (2019a). Evaluation. Press.")]
        mentions = build_citations(blocks, body(blocks))["mentions"]
        self.assertEqual([m["status"] for m in mentions], ["ambiguous", "ambiguous", "matched", "unresolved", "unresolved"])
        self.assertEqual(mentions[0]["reference_ids"], [])
        self.assertEqual(mentions[2]["reference_ids"], ["ref-0003"])

    def test_bibliography_fallback_appendix_and_typed_lists(self):
        blocks = [text("Works [1]."), text("2. References"), text("[1] A. Doe. Work."),
                  text("Appendix A"), text("More detail on [1].")]
        self.assertEqual(bibliography_indices(blocks), {1, 2})
        result = build_citations(blocks, body(blocks))
        self.assertEqual([m["block_index"] for m in result["mentions"]], [0, 4])
        blocks = [text("Works [1, 2]."),
                  {"type": "list", "sub_type": "ref_text", "list_items": [" 1 Doe, First.", "2 Brown, Second."]}]
        result = build_citations(blocks, body(blocks))
        self.assertEqual(result["references"][0]["source_spans"][0],
                         {"block_index": 1, "field": "list_items[0]", "page": None, "start": 1, "end": 14})
        self.assertEqual(result["mentions"][0]["status"], "matched")

    def test_formula_code_and_html_offsets(self):
        blocks = [text("$A[7] + [3]$ and `[5]` in [1](url)."),
                  {"type": "table", "table_body": "<table><tr><td>Prior [1]</td></tr></table>"}, reference("[1] A source.")]
        units = body(blocks) + [{"text": "<tr><td>Prior [1]</td></tr>", "field": "table_body", "field_offset": 7,
                                 "block_index": 1, "page": 1, "section_id": "s1"}]
        mention, = build_citations(blocks, units)["mentions"]
        start, end = (mention["field_offset"] + mention[k] for k in ("start", "end"))
        self.assertEqual(blocks[1]["table_body"][start:end], mention["marker"])
        self.assertEqual(mention["reference_ids"], ["ref-0001"])

    def test_chinese_numeric_punctuation_keeps_original_marker(self):
        blocks = [text("方法不同。该综述比较了两篇工作［1，2］。"), text("参考文献", text_level=1),
                  reference("［1］第一篇文章。"), reference("［2］第二篇文章。")]
        mention, = build_citations(blocks, body(blocks))["mentions"]
        self.assertEqual(mention["marker"], "［1，2］")
        self.assertEqual(mention["context"], "该综述比较了两篇工作［1，2］。")
        self.assertEqual(mention["reference_ids"], ["ref-0001", "ref-0002"])


if __name__ == "__main__":
    unittest.main()
