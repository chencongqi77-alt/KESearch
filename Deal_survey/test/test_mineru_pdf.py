from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from pypdf import PdfWriter

from deal_survey import mineru_pdf


def write_pdf(path, pages):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(200, 300)
    writer.write(path)


def result_zip(origin=None):
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("parse_content_list.json", json.dumps([{"type": "text", "text": "body", "page_idx": 0}]))
        archive.writestr("parse_content_list_v2.json", "[[]]")
        archive.writestr("full.md", b"Original Markdown\r\n")
        if origin is not None:
            archive.writestr("parse_origin.pdf", origin)
    return output.getvalue()


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.pages = None
        self.batch_id = "batch-1"
        self.upload_url = "https://storage.example/up?signature=test-signature"
        self.download_url = "https://storage.example/down?signature=test-signature"
        self.package = result_zip(b"provider re-encoded the original PDF")
        self.interrupt_submit = False
        self.interrupt_upload = False
        self.interrupt_poll = False
        self.waiting = False

    def submit(self, data_id, *, deadline, max_pages):
        self.calls.append("submit")
        self.pages = max_pages
        if self.interrupt_submit:
            raise OSError(self.upload_url)
        return {"batch_id": self.batch_id, "upload_url": self.upload_url}

    def upload(self, url, raw, *, deadline):
        self.calls.append("upload")
        self.uploaded = raw
        if self.interrupt_upload:
            raise TimeoutError(url)

    def poll(self, batch_id, *, data_id, deadline):
        self.calls.append("poll")
        if self.interrupt_poll:
            raise TimeoutError(self.download_url)
        if self.waiting:
            return {"state": "waiting-file"}
        return {"state": "done", "full_zip_url": self.download_url, "extract_progress": {"total_pages": self.pages}}

    def result(self, url, *, deadline):
        self.calls.append("result")
        return self.package


class MinerUPdfTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.pdf = self.directory / "survey.pdf"
        write_pdf(self.pdf, 2)
        self.cloud = self.directory / "cloud"
        self.provider = FakeProvider()

    def parse(self, **options):
        return mineru_pdf.parse_pdf(self.pdf, self.cloud, provider=self.provider, **options)

    def test_resume_known_batch_single_upload_and_offline_reuse(self):
        self.provider.interrupt_poll = True
        with self.assertRaises(TimeoutError):
            self.parse()
        self.provider.interrupt_poll = False
        result = self.parse()
        self.assertEqual(self.provider.calls, ["submit", "upload", "poll", "poll", "result"])
        self.assertEqual(self.provider.uploaded, self.pdf.read_bytes())
        self.assertEqual(self.provider.pages, 2)
        with patch.object(mineru_pdf, "_live_provider", side_effect=AssertionError):
            self.assertEqual(mineru_pdf.parse_pdf(self.pdf, self.cloud), result)
        self.assertEqual(Path(result["markdown_path"]).read_bytes(), b"Original Markdown\r\n")
        blocks, meta = mineru_pdf.load_parse(self.pdf, result["result_zip"])
        self.assertEqual(blocks[0]["text"], "body")
        self.assertEqual(meta["identity_basis"], "receipt_source_and_zip_sha256")
        self.assertFalse(meta["origin_bytes_equal"])
        self.assertEqual(meta["page_scope"], "full_document_requested")
        for name in ("state.json", "result.json"):
            self.assertNotIn("test-signature", (self.cloud / name).read_text(encoding="utf-8"))

    def test_unknown_submission_never_submits_again_or_exposes_signed_url(self):
        self.provider.interrupt_submit = True
        with self.assertRaisesRegex(ValueError, "请求失败") as failure:
            self.parse()
        self.assertNotIn("signature", str(failure.exception))
        with self.assertRaisesRegex(ValueError, "结果不明"):
            self.parse()
        self.assertEqual(self.provider.calls, ["submit"])

    def test_lost_upload_url_keeps_same_batch_and_can_resume_when_cloud_has_it(self):
        self.provider.interrupt_upload = True
        with self.assertRaises(TimeoutError) as failure:
            self.parse()
        self.assertNotIn("signature", str(failure.exception))
        self.provider.waiting = True
        with self.assertRaisesRegex(ValueError, "等待文件"):
            self.parse()
        self.provider.waiting = False
        self.assertEqual(self.parse()["batch_id"], self.provider.batch_id)
        self.assertEqual(self.provider.calls, ["submit", "upload", "poll", "poll", "result"])

    def test_conflicting_input_and_model_rejected_before_additional_requests(self):
        self.parse()
        calls = self.provider.calls.copy()
        with self.assertRaisesRegex(ValueError, "不匹配"):
            self.parse(model="pipeline")
        write_pdf(self.pdf, 3)
        with self.assertRaisesRegex(ValueError, "不匹配"):
            self.parse()
        self.assertEqual(self.provider.calls, calls)

    def test_oversize_document_does_not_submit_first_200_pages(self):
        write_pdf(self.pdf, 201)
        with self.assertRaisesRegex(ValueError, "200"):
            self.parse()
        self.assertFalse(self.cloud.exists())
        self.assertEqual(self.provider.calls, [])

    def test_replay_requires_matching_source_and_archive_and_full_page_receipt(self):
        result = self.parse()
        archive = Path(result["result_zip"])
        partial = self.directory / "receipt.json"
        for field, value in (("source_sha256", "0" * 64), ("zip_sha256", "0" * 64),
                             ("requested_pages", 1), ("pdf_pages", 1), ("provider_total_pages", 1),
                             ("full_document_requested", False)):
            with self.subTest(field=field):
                partial.write_text(json.dumps({**result, field: value}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    mineru_pdf.load_parse(self.pdf, archive, receipt_path=partial)
        archive.write_bytes(archive.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "指纹不匹配"):
            mineru_pdf.load_parse(self.pdf, archive)
        with self.assertRaisesRegex(ValueError, "指纹不匹配"):
            self.parse()

    def test_no_receipt_requires_matching_origin_and_leaves_page_scope_unverified(self):
        archive = self.directory / "copy.zip"
        for origin in (None, b"unrelated"):
            archive.write_bytes(result_zip(origin))
            with self.assertRaisesRegex(ValueError, "同字节原件"):
                mineru_pdf.load_parse(self.pdf, archive)
        archive.write_bytes(result_zip(self.pdf.read_bytes()))
        _, meta = mineru_pdf.load_parse(self.pdf, archive)
        self.assertTrue(meta["origin_bytes_equal"])
        self.assertEqual(meta["page_scope"], "unverified")
        self.assertEqual(meta["content_list_member"], "parse_content_list.json")


if __name__ == "__main__":
    unittest.main()
