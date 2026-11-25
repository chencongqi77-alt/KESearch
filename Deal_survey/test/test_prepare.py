import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from pypdf import PdfWriter

from deal_survey.prepare import prepare
from deal_survey.structure import locate_passages


def text(value, *, level=None, page=0):
    block = {"type": "text", "text": value, "page_idx": page}
    if level:
        block["text_level"] = level
    return block


class SurveyPreparationTests(unittest.TestCase):
    def test_bookmarks_and_numbering_restore_the_tree_and_table_offsets(self):
        blocks = [text("Survey of Methods", level=1), text("3 Methods", level=2),
                  text("3.1 Encoders", level=2), text("Variants", level=2),
                  {"type": "table", "page_idx": 1,
                   "table_body": "<table><tr><td>System</td></tr><tr><td>Fast [8]</td></tr></table>"},
                  text("4 Conclusion", level=2), text("Short note [8].")]
        sections, units, _ = locate_passages(blocks, set(), [(3, "Variants", 1)])
        self.assertEqual([s["level"] for s in sections], [0, 1, 2, 3, 1])
        self.assertEqual(sections[3]["path"], ["3 Methods", "3.1 Encoders", "Variants"])
        table = next(u for u in units if "Fast" in u["text"])
        self.assertEqual(table["section_id"], sections[3]["id"])
        self.assertEqual(table["page"], 2)
        self.assertTrue(blocks[4]["table_body"][table["field_offset"]:].startswith(table["text"]))
        self.assertEqual(units[-1]["section_id"], sections[-1]["id"])

    def test_pack_has_forward_and_reverse_views_and_verbatim_locations(self):
        blocks = [text("Survey of Methods", level=1), text("1 Methods", level=2),
                  text("1.1 Sparse variants", level=2),
                  text("We contrast two sparse models [1, 2]. Another paper [1] studies retrieval."),
                  text("2 Evaluation", level=2), text("We evaluate the second model [2]."),
                  text("References", level=2)]
        blocks.extend({"type": "ref_text", "page_idx": 0, "text": f'[{i}] A. Example, “Model {i},” 2020.'}
                      for i in (1, 2, 3))
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pdf, archive = base / "survey.pdf", base / "result.zip"
            writer = PdfWriter()
            writer.add_blank_page(width=500, height=500)
            with pdf.open("wb") as stream:
                writer.write(stream)
            with ZipFile(archive, "w") as bundle:
                bundle.writestr("source_origin.pdf", pdf.read_bytes())
                bundle.writestr("example_content_list.json", json.dumps(blocks))
            out = base / "work"
            final, counts = prepare(pdf, out, archive=archive)
            pack = json.loads((final / "survey.json").read_bytes())
            self.assertEqual((counts["markers"], counts["cited_entries"], counts["bibliography_entries"]), (3, 2, 3))
            parent, child = pack["sections"][1:3]
            self.assertEqual(parent["reference_ids"], [])
            self.assertEqual(parent["subtree_reference_ids"], child["reference_ids"])
            self.assertEqual(len(pack["references"][1]["section_ids"]), 2)
            self.assertEqual(pack["references"][2]["mention_ids"], [])
            for mention in pack["mentions"]:
                unit = blocks[mention["block_index"]]["text"]
                self.assertEqual(unit[mention["start"]:mention["end"]], mention["marker"])
                self.assertEqual(unit[mention["context_start"]:mention["context_end"]], mention["context"])
            self.assertEqual(pack["pdf_check"]["status"], "unverified")
            article = (final / "reading.md").read_text(encoding="utf-8")
            self.assertIn("1 Methods › 1.1 Sparse variants", article)
            self.assertIn("We contrast two sparse models [1, 2].", article)
            with self.assertRaises(FileExistsError):
                prepare(pdf, out, archive=archive)
            self.assertEqual(article, (final / "reading.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
