"""Exercise the public workbench endpoints in an isolated local HTTP server."""

from http.client import HTTPConnection
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import quote

from deal_survey import mineru_pdf, reader
from deal_survey.server import JobStore, make_server, process_job

from .test_mineru_pdf import FakeProvider, write_pdf


def _json_file(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.web = self.root / "web"
        self.web.mkdir()
        (self.web / "index.html").write_text("工作台", encoding="utf-8")
        self.enter = threading.Event()
        self.release = threading.Event()
        self.release.set()
        self.fail_once = False
        self.calls = []
        self.figure = "5" * 64 + ".png"
        self.figure_bytes = b"\x89PNG\r\n\x1a\nexample"
        self.start()
        self.addCleanup(self.stop)

    def start(self):
        self.server = make_server(self.state, 0, processor=self.process, web_root=self.web)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .02})
        self.thread.start()

    def stop(self):
        if self.server:
            self.release.set()
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
            self.server = None

    def process(self, folder, progress, summary_only):
        self.calls.append(summary_only)
        progress("summary" if summary_only else "mineru")
        self.enter.set()
        if not self.release.wait(timeout=5):
            raise TimeoutError()
        if self.fail_once:
            self.fail_once = False
            raise OSError("example-signed-url-must-not-escape")
        if not summary_only:
            (folder / "cloud").mkdir()
            (folder / "cloud" / "full.md").write_bytes(b"# Example")
            (folder / "assets").mkdir()
            (folder / "assets" / self.figure).write_bytes(self.figure_bytes)
            (folder / "assets" / ("0" * 64 + ".gif")).write_bytes(b"<!doctype html>bad")
        _json_file(folder / "reader.json", {"title": "Example", "summary": {
            "source": "deepseek" if summary_only else "extract", "text": "Evidence"}})
        return "Example"

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            data = response.read()
            if response.getheader("Content-Type", "").startswith("application/json"):
                data = json.loads(data)
            return response.status, data, dict(response.getheaders())
        finally:
            connection.close()

    def wait(self, path, status):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            code, data, _ = self.request("GET", path)
            if code == 200 and data["status"] == status:
                return data
            time.sleep(.01)
        self.fail(f"did not reach {status}")

    def upload(self):
        status, job, _ = self.request("POST", "/api/jobs?filename=" + quote("测试 1.pdf"),
                                      b"%PDF-synthetic", {"Content-Type": "application/pdf"})
        self.assertEqual(status, 202)
        self.assertEqual(job["filename"], "测试 1.pdf")
        return "/api/jobs/" + job["id"]

    def test_public_upload_read_links_and_persistence(self):
        self.assertEqual(self.request("GET", "/")[1].decode(), "工作台")
        path = self.upload()
        job = self.wait(path, "ready")
        self.assertTrue(job["has_markdown"] and job["has_pdf"] and job["has_reader"])
        self.assertEqual(self.request("GET", path + "/reader")[1]["title"], "Example")
        self.assertEqual(self.request("GET", path + "/pdf")[1], b"%PDF-synthetic")
        status, body, headers = self.request("GET", path + "/markdown")
        self.assertEqual((status, body), (200, b"# Example"))
        self.assertTrue(headers["Content-Disposition"].startswith("attachment;"))
        self.assertEqual(self.request("GET", path + "/assets/" + self.figure)[1], self.figure_bytes)
        for filename in ("0" * 64 + ".gif", "../source.pdf", "%2e%2e%2fsource.pdf", "job.json"):
            self.assertEqual(self.request("GET", path + "/assets/" + filename)[0], 404)
        self.stop()
        self.start()
        self.assertEqual(self.request("GET", "/api/jobs")[1]["jobs"][0], job)

    def test_failed_submission_is_redacted_and_retried_once(self):
        self.fail_once = True
        path = self.upload()
        job = self.wait(path, "failed")
        self.assertNotIn("signed-url", job["message"])
        self.assertEqual(self.request("GET", path + "/reader")[0], 409)
        self.enter.clear()
        self.release.clear()
        self.assertEqual(self.request("POST", path + "/retry")[0], 202)
        self.assertTrue(self.enter.wait(timeout=1))
        self.assertEqual(self.request("POST", path + "/retry")[0], 409)
        self.release.set()
        self.wait(path, "ready")
        self.assertEqual(self.calls, [False, False])

    def test_retry_only_summary_keeps_existing_document_readable(self):
        path = self.upload()
        self.wait(path, "ready")
        self.enter.clear()
        self.release.clear()
        self.assertEqual(self.request("POST", path + "/retry")[0], 202)
        self.assertTrue(self.enter.wait(timeout=1))
        self.assertEqual(self.request("GET", path + "/reader")[1]["summary"]["source"], "extract")
        self.release.set()
        self.wait(path, "ready")
        self.assertEqual(self.request("GET", path + "/reader")[1]["summary"]["source"], "deepseek")
        self.assertEqual(self.request("POST", path + "/retry")[0], 409)
        self.assertEqual(self.calls, [False, True])

    def add_link_reader(self):
        path = self.upload()
        self.wait(path, "ready")
        folder = self.state / path.rsplit("/", 1)[1]
        article = self.request("GET", path + "/reader")[1]
        article["references"] = [
            {"id": "a", "link_kind": "doi", "url": "https://doi.org/10.0000/a"},
            {"id": "b", "link_kind": "arxiv_search", "url": "https://arxiv.org/search/?query=b"},
        ]
        _json_file(folder / "reader.json", article)
        return path, folder, article

    def wait_link_check(self, path, status):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            job = self.request("GET", path)[1]
            if job.get("link_check", {}).get("status") == status:
                return job
            time.sleep(.01)
        self.fail(f"link check did not reach {status}")

    def test_recheck_only_links_keeps_reader_open_and_persists_result(self):
        path, _, article = self.add_link_reader()
        self.enter.clear()
        self.release.clear()

        def lookup(document):
            self.enter.set()
            if not self.release.wait(timeout=3):
                raise TimeoutError()
            document["references"][1].update(link_kind="arxiv", url="https://arxiv.org/abs/2001.00001")
            return {"resolved": 1, "remaining": 0, "status": "complete", "message": "已核对 1 篇"}

        with patch.object(reader, "refresh_reference_links", side_effect=lookup) as resolver:
            self.assertEqual(self.request("GET", path + "/recheck-links")[0], 405)
            code, job, _ = self.request("POST", path + "/recheck-links")
            self.assertEqual((code, job["status"], job["link_check"]["status"]), (202, "ready", "queued"))
            self.assertTrue(self.enter.wait(1))
            self.assertEqual(self.request("GET", path + "/reader")[1], article)
            self.assertEqual(self.request("GET", "/api/jobs")[1]["jobs"][0]["link_check"]["status"], "running")
            self.assertEqual(self.request("POST", path + "/recheck-links")[0], 409)
            self.assertEqual(self.request("POST", path + "/retry")[0], 409)
            self.release.set()
            final = self.wait_link_check(path, "complete")
        self.assertEqual(final["link_check"]["resolved"], 1)
        result = self.request("GET", path + "/reader")[1]
        self.assertEqual(result["summary"], article["summary"])
        self.assertEqual(result["references"][0], article["references"][0])
        self.assertEqual(result["references"][1]["link_kind"], "arxiv")
        resolver.assert_called_once()
        self.assertEqual(self.calls, [False])
        self.stop()
        self.start()
        self.assertEqual(self.request("GET", path)[1], final)
        self.assertEqual(self.request("POST", path + "/recheck-links")[0], 409)

    def test_interrupted_link_check_resumes_and_timeout_keeps_prior_reader(self):
        path, folder, article = self.add_link_reader()
        self.stop()
        job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
        job["link_check"] = {"status": "running", "total": 1, "resolved": 0, "remaining": 1, "message": ""}
        _json_file(folder / "job.json", job)
        with patch.object(reader, "refresh_reference_links", side_effect=TimeoutError("secret URL")) as resolver:
            self.start()
            failed = self.wait_link_check(path, "failed")
        self.assertEqual(failed["status"], "ready")
        self.assertIn("超时", failed["link_check"]["message"])
        self.assertNotIn("secret", failed["link_check"]["message"])
        self.assertEqual(self.request("GET", path + "/reader")[1], article)
        resolver.assert_called_once()
        partial = {"resolved": 0, "remaining": 1, "status": "partial", "message": "未找到唯一匹配。"}
        # Earlier readers stored the same paper only in individual chapter snapshots.
        ref = article.pop("references")[1]
        article["sections"] = [{"references": [ref]}, {"references": [ref]}]
        _json_file(folder / "reader.json", article)
        with patch.object(reader, "refresh_reference_links", return_value=partial):
            self.assertEqual(self.request("POST", path + "/recheck-links")[0], 202)
            self.assertEqual(self.wait_link_check(path, "partial")["link_check"], {"total": 1, **partial})
        self.assertEqual(self.calls, [False])

    def test_upload_validation_fails_before_creating_jobs(self):
        path = "/api/jobs?filename=f.pdf"
        headers = {"Content-Type": "application/pdf"}
        cases = [
            (path, b"%PDF-", {**headers, "Origin": "https://external.example"}, 403),
            (path, b"%PDF-", {**headers, "Host": "external.example"}, 403),
            (path, b"%PDF-", {"Content-Type": "text/plain"}, 415),
            (path, b"%PDF-", {**headers, "Content-Length": "999999999"}, 413),
            (path, b"plain", headers, 400),
            ("/api/jobs?filename=..%2ff.pdf", b"%PDF-", headers, 400),
        ]
        for target, content, names, expected in cases:
            with self.subTest(target=target, names=names):
                self.assertEqual(self.request("POST", target, content, names)[0], expected)
        self.assertEqual(self.request("GET", "/api/jobs")[1], {"jobs": []})
        self.assertEqual(self.calls, [])

    def test_one_owner_per_workspace_and_interrupted_jobs_can_continue(self):
        with self.assertRaisesRegex(ValueError, "另一个服务"):
            JobStore(self.state, self.process)
        self.stop()
        key = "8" * 32
        folder = self.state / key
        folder.mkdir()
        _json_file(folder / "job.json", {"id": key, "filename": "a.pdf", "title": "a", "status": "running",
                                         "stage": "mineru", "message": "", "created_at": "2026-01-01"})
        (folder / "source.pdf").write_bytes(b"%PDF-test")
        self.start()
        path = "/api/jobs/" + key
        self.assertEqual(self.request("GET", path)[1]["status"], "failed")
        self.assertEqual(self.request("POST", path + "/retry")[0], 202)
        self.wait(path, "ready")

    def test_real_worker_connects_mineru_markdown_to_deepseek_reader(self):
        self.server.store.processor = process_job
        pdf = self.root / "Sample.pdf"
        write_pdf(pdf, 1)
        provider = FakeProvider()
        answer = {"choices": [{"finish_reason": "stop", "message": {"content": "综述总结。"}}]}
        with (patch.object(mineru_pdf, "_live_provider", return_value=provider),
              patch.object(reader, "_fetch", return_value=json.dumps(answer).encode()) as fetch,
              patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-test-key",
                                      "KET_DEEPSEEK_BASE_URL": "https://api.deepseek.com", "KET_MINERU_MODEL": "vlm"})):
            code, job, _ = self.request("POST", "/api/jobs?filename=Sample.pdf", pdf.read_bytes(),
                                        {"Content-Type": "application/pdf"})
            self.assertEqual(code, 202)
            path = "/api/jobs/" + job["id"]
            self.wait(path, "ready")
            self.assertEqual(self.request("GET", path + "/markdown")[1], b"Original Markdown\r\n")
            article = self.request("GET", path + "/reader")[1]
            self.assertEqual((article["title"], article["summary"]["text"]), ("Sample", "综述总结。"))
            self.assertEqual(provider.calls, ["submit", "upload", "poll", "result"])
            self.assertEqual(fetch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
