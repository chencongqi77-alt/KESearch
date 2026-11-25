"""Local HTTP workbench for reading one MinerU-parsed survey at a time."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from http.client import HTTPConnection, HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from queue import Queue
import re
import shutil
import socket
import tempfile
import threading
from urllib.parse import parse_qs, quote, urlsplit
from uuid import uuid4

from .mineru_pdf import MAX_PDF_BYTES, _write_json, parse_pdf
from .prepare import prepare
from .settings import DIRECTORY as ROOT, load_service_env


WEB_ROOT = Path(__file__).resolve().with_name("web")
JOB_ID = re.compile(r"[0-9a-f]{32}")
ASSET = re.compile(r"[0-9a-f]{64}\.(png|jpg|gif|webp)")
IMAGE_TYPES = {"png": "image/png", "jpg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
STAGES = {
    "queued": "已加入解析队列",
    "mineru": "MinerU 正在解析整篇 PDF",
    "structure": "正在整理章节、书目和综述原文",
    "summary": "正在核对论文链接并生成综述摘要",
    "ready": "可以阅读",
}


class RequestError(Exception):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _checking_links(job):
    return job.get("link_check", {}).get("status") in {"queued", "running"}


@contextmanager
def _workspace_lock(root):
    # OS-owned locks are released when the service stops, including after a crash.
    with (root / ".service.lock").open("a+b") as handle:
        try:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValueError("该工作台目录已由另一个服务使用") from None
        yield


def process_job(folder, progress, summary_only=False):
    from .reader import build_reader, summarize_reader
    reader_path = folder / "reader.json"
    if summary_only:
        progress("summary", "正在重试 DeepSeek 摘要")
        reader = _load_json(reader_path)
        reader["summary"] = summarize_reader(reader)
    else:
        pdf = folder / "source.pdf"
        progress("mineru")
        receipt = parse_pdf(pdf, folder / "cloud", model=os.environ.get("KET_MINERU_MODEL") or "vlm")
        archive = Path(receipt["result_zip"])
        progress("structure")
        reading = folder / "reading"
        if not reading.is_dir():
            prepare(pdf, folder, archive=archive)
        pack = _load_json(reading / "survey.json")
        filename = _load_json(folder / "job.json")["filename"]
        pack["source"]["pdf_name"] = filename
        if not pack["sections"][0]["title"]:
            pack["title"] = Path(filename).stem
        progress("summary")
        reader = build_reader(pack, archive, folder / "assets",
                              asset_url_prefix=f"/api/jobs/{folder.name}/assets/", summarize=True)
    _write_json(reader_path, reader)
    return reader["title"]


def _failure_message(stage, error):
    # Third-party exceptions can include signed URLs, request content, or tokens.
    if isinstance(error, TimeoutError):
        return "等待服务响应超时，可以重试以继续当前任务。"
    if stage == "mineru":
        safe_errors = {
            "输入 PDF 没有页", "无法读取输入 PDF 的页数", "当前整篇上传支持最多 200 页",
            "该云批次已失败", "MinerU 云批次解析失败", "上次云提交结果不明，无法安全地再次提交",
            "已有云批次仍等待文件，原签名上传地址未保存，不能自动重提",
            "云端解析需要进程环境变量 KET_MINERU_API_TOKEN",
        }
        detail = str(error)
        if detail in safe_errors:
            return detail
        if re.fullmatch(r"MinerU 请求失败（(?:unauthorized|forbidden|rate_limited|network_or_tls_error|dns_failed|connection_failed|http_request_failed|provider_rejected)）", detail):
            return detail
        if isinstance(error, ModuleNotFoundError) and error.name == "pypdf":
            return "运行环境缺少 pypdf，请使用已安装项目依赖的 Python 启动。"
        return "MinerU 未能完成解析，请检查服务配置及上传的 PDF。"
    if stage == "structure":
        return "章节与引文整理失败，请核对 MinerU 的解析结果后重试。"
    return "阅读内容生成失败，请重试当前任务。"


class JobStore:
    def __init__(self, root, processor=process_job):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.processor = processor
        self.guard = threading.RLock()
        self.queue = Queue()
        self.jobs = {}
        self.stopping = False
        self.lock = _workspace_lock(self.root)
        self.lock.__enter__()
        try:
            for folder in self.root.iterdir():
                if not JOB_ID.fullmatch(folder.name) or not folder.is_dir() or folder.is_symlink():
                    continue
                path = folder / "job.json"
                if not path.is_file():
                    continue
                job = _load_json(path)
                if job["id"] != folder.name:
                    raise ValueError("工作台任务记录与目录不一致")
                self.jobs[job["id"]] = job
                if job["status"] in {"queued", "running"}:
                    self._set(job["id"], "failed", "failed", "服务已重启，可继续当前任务。")
                if _checking_links(job):
                    self._save(job["id"], link_check={**job["link_check"], "status": "queued",
                                                      "message": "等待继续核对论文链接"})
                    self.queue.put((job["id"], "links"))
            self.worker = threading.Thread(target=self._work, name="survey-processor", daemon=True)
            self.worker.start()
        except BaseException:
            self.lock.__exit__(None, None, None)
            raise

    def close(self):
        with self.guard:
            if not self.stopping:
                self.stopping = True
                self.queue.put(None)
        self.worker.join(timeout=1)

    def _save(self, job_id, **changes):
        with self.guard:
            job = {**self.jobs[job_id], **changes}
            _write_json(self.root / job_id / "job.json", job)
            self.jobs[job_id] = job

    def _set(self, job_id, status, stage, message, **extra):
        self._save(job_id, status=status, stage=stage, message=message, **extra)

    def get(self, job_id):
        with self.guard:
            job = self.jobs.get(job_id)
            if job is None:
                raise RequestError(404, "未找到该任务")
            folder = self.root / job_id
            return {**job, "has_reader": (folder / "reader.json").is_file(),
                    "has_markdown": (folder / "cloud" / "full.md").is_file(),
                    "has_pdf": (folder / "source.pdf").is_file()}

    def list(self):
        with self.guard:
            return sorted((self.get(key) for key in self.jobs), key=lambda j: j["created_at"], reverse=True)

    def upload(self, stream, length, filename):
        if length < 5 or length > MAX_PDF_BYTES:
            raise RequestError(413 if length > MAX_PDF_BYTES else 400, "请选择 200 MiB 以内的 PDF 文件")
        if (not filename or len(filename) > 255 or not filename.lower().endswith(".pdf")
                or "/" in filename or "\\" in filename or any(not c.isprintable() for c in filename)):
            raise RequestError(400, "请提供有效的 PDF 文件名")
        if stream.read(5) != b"%PDF-":
            raise RequestError(400, "文件没有有效的 PDF 文件头")
        job_id = uuid4().hex
        with tempfile.TemporaryDirectory(dir=self.root, prefix=".upload-") as temp:
            pending = Path(temp) / job_id
            pending.mkdir()
            with (pending / "source.pdf").open("wb") as target:
                target.write(b"%PDF-")
                remaining = length - 5
                while remaining:
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise RequestError(400, "PDF 上传中断，请重新选择文件")
                    target.write(chunk)
                    remaining -= len(chunk)
            job = {"id": job_id, "filename": filename, "title": Path(filename).stem,
                   "status": "queued", "stage": "queued", "message": STAGES["queued"],
                   "created_at": datetime.now(timezone.utc).isoformat(timespec="microseconds")}
            _write_json(pending / "job.json", job)
            with self.guard:
                pending.rename(self.root / job_id)
                self.jobs[job_id] = job
                self.queue.put((job_id, "parse"))
                return self.get(job_id)

    def retry(self, job_id):
        with self.guard:
            job = self.get(job_id)
            if job["status"] not in {"ready", "failed"} or _checking_links(job):
                raise RequestError(409, "任务仍在处理中")
            reader_path = self.root / job_id / "reader.json"
            summary_only = reader_path.is_file()
            if job["status"] == "ready":
                if not summary_only or _load_json(reader_path)["summary"]["source"] == "deepseek":
                    raise RequestError(409, "该任务已完成")
            self._set(job_id, "queued", "queued", STAGES["queued"])
            self.queue.put((job_id, "summary" if summary_only else "parse"))
            return self.get(job_id)

    def recheck_links(self, job_id):
        from .reader import reference_catalogue
        with self.guard:
            job = self.get(job_id)
            if job["status"] not in {"ready", "failed"} or _checking_links(job):
                raise RequestError(409, "任务正在处理中，请等待当前操作完成")
            if not job["has_reader"]:
                raise RequestError(409, "请先完成综述解析")
            reader = _load_json(self.root / job_id / "reader.json")
            remaining = sum(ref.get("link_kind") == "arxiv_search" for ref in reference_catalogue(reader).values())
            if not remaining:
                raise RequestError(409, "没有待核对的检索入口")
            self._save(job_id, link_check={"status": "queued", "total": remaining, "remaining": remaining,
                                          "resolved": 0, "message": "已加入论文链接核对队列"})
            self.queue.put((job_id, "links"))
            return self.get(job_id)

    def _run_link_check(self, job_id):
        reader_path = self.root / job_id / "reader.json"
        check = self.get(job_id)["link_check"]
        self._save(job_id, link_check={**check, "status": "running", "message": "正在核对全篇的论文链接…"})
        try:
            from .reader import refresh_reference_links
            reader = _load_json(reader_path)
            result = refresh_reference_links(reader)
            # On restart a previous attempt may already have published its reader.
            saved_before_restart = check["total"] - result["remaining"] - result["resolved"]
            if saved_before_restart > 0:
                result["resolved"] += saved_before_restart
                result["message"] += f"服务重启前另已保存 {saved_before_restart} 篇。"
                if result["status"] == "failed":
                    result["status"] = "partial"
            with self.guard:
                _write_json(reader_path, reader)
                self._save(job_id, link_check={"total": check["total"], **result})
        except Exception as error:
            message = "论文链接核对超时，可以重试。" if isinstance(error, TimeoutError) else "论文链接核对失败，可以重试。"
            self._save(job_id, link_check={**check, "status": "failed", "message": message})

    def _work(self):
        try:
            while True:
                item = self.queue.get()
                if item is None or self.stopping:
                    return
                job_id, operation = item
                if operation == "links":
                    self._run_link_check(job_id)
                    continue

                def progress(stage, message=None):
                    self._set(job_id, "running", stage, message or STAGES[stage])

                try:
                    title = self.processor(self.root / job_id, progress, operation == "summary")
                    self._set(job_id, "ready", "ready", STAGES["ready"], title=title)
                except Exception as error:
                    stage = self.get(job_id)["stage"]
                    self._set(job_id, "failed", "failed", _failure_message(stage, error))
        finally:
            self.lock.__exit__(None, None, None)


class SurveyHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, store, web_root):
        self.store = store
        self.web_root = Path(web_root).resolve()
        super().__init__(address, SurveyHandler)

    def server_close(self):
        super().server_close()
        self.store.close()


class SurveyHandler(BaseHTTPRequestHandler):
    server_version = "SurveyReader"
    sys_version = ""
    timeout = 60

    def log_message(self, format, *args):
        pass

    def _headers(self, status, mime, length):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, mime, *, disposition=None, check_image=None):
        if not path.is_file() or path.is_symlink():
            raise RequestError(404, "未找到该文件")
        with path.open("rb") as source:
            if check_image:
                head = source.read(12)
                signatures = {"png": head.startswith(b"\x89PNG\r\n\x1a\n"), "jpg": head.startswith(b"\xff\xd8\xff"),
                              "gif": head.startswith((b"GIF87a", b"GIF89a")),
                              "webp": head.startswith(b"RIFF") and head[8:12] == b"WEBP"}
                if not signatures[check_image]:
                    raise RequestError(404, "未找到可展示的原图")
                source.seek(0)
            self._headers(200, mime, os.fstat(source.fileno()).st_size)
            if disposition:
                self.send_header("Content-Disposition", disposition)
            self.end_headers()
            shutil.copyfileobj(source, self.wfile, 128 * 1024)

    def _handle(self):
        try:
            # Local-only Host and Origin checks keep foreign pages from starting paid jobs.
            host = self.headers.get("Host", "").lower()
            port = self.server.server_port
            hosts = {f"localhost:{port}", f"127.0.0.1:{port}"}
            if port == 80:
                hosts.update(("localhost", "127.0.0.1"))
            if host not in hosts:
                raise RequestError(403, "仅支持本机工作台访问")
            origin = self.headers.get("Origin")
            if origin and origin.lower() != "http://" + host:
                raise RequestError(403, "请从工作台页面提交请求")
            self._route()
        except RequestError as error:
            self._json(error.status, {"error": str(error)})
            if self.command == "POST":
                # Windows may reset a socket closed with unread upload bytes. Deliver the
                # complete rejection first, then consume the small, already-arriving body.
                try:
                    self.connection.shutdown(socket.SHUT_WR)
                    self.connection.settimeout(.1)
                    self.rfile.read1(64 * 1024)
                except OSError:
                    pass
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            self.close_connection = True
        except Exception:
            self._json(500, {"error": "工作台请求失败，请检查本地运行目录"})

    do_GET = do_POST = _handle

    def _route(self):
        url = urlsplit(self.path)
        path = url.path
        store = self.server.store
        if path == "/api/jobs":
            if self.command == "GET":
                return self._json(200, {"jobs": store.list()})
            if self.headers.get_content_type() != "application/pdf":
                raise RequestError(415, "请以 application/pdf 上传 PDF")
            lengths = self.headers.get_all("Content-Length", [])
            if (len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,12}", lengths[0])
                    or self.headers.get("Transfer-Encoding")):
                raise RequestError(411, "请提供 PDF 文件长度")
            filename = parse_qs(url.query).get("filename", [""])[0]
            return self._json(202, store.upload(self.rfile, int(lengths[0]), filename))
        match = re.fullmatch(r"/api/jobs/([0-9a-f]{32})(?:/(reader|markdown|pdf|retry|recheck-links|assets/[^/]+))?", path)
        if match:
            job_id, resource = match.groups()
            job = store.get(job_id)
            folder = store.root / job_id
            if self.command == "POST":
                if resource == "retry":
                    return self._json(202, store.retry(job_id))
                if resource == "recheck-links":
                    return self._json(202, store.recheck_links(job_id))
                raise RequestError(405, "该入口只支持读取")
            if resource is None:
                return self._json(200, job)
            if resource in {"retry", "recheck-links"}:
                raise RequestError(405, "请使用 POST 提交任务")
            if resource == "reader":
                if not job["has_reader"]:
                    raise RequestError(409, "阅读内容尚未生成")
                # Close the read handle before a recheck publishes a replacement on Windows.
                with store.guard:
                    reader_path = folder / "reader.json"
                    if reader_path.is_symlink():
                        raise RequestError(404, "未找到该文件")
                    body = reader_path.read_bytes()
                self._headers(200, "application/json; charset=utf-8", len(body))
                self.end_headers()
                self.wfile.write(body)
                return
            if resource == "markdown":
                name = quote(Path(job["filename"]).stem + ".md")
                return self._file(folder / "cloud" / "full.md", "text/markdown; charset=utf-8",
                                  disposition="attachment; filename*=UTF-8''" + name)
            if resource == "pdf":
                return self._file(folder / "source.pdf", "application/pdf",
                                  disposition="inline; filename*=UTF-8''" + quote(job["filename"]))
            assets = folder / "assets"
            name = resource.removeprefix("assets/")
            image = ASSET.fullmatch(name)
            if image and not assets.is_symlink():
                ext = image.group(1)
                return self._file(assets / name, IMAGE_TYPES[ext], check_image=ext)
        if self.command == "GET":
            static = "index.html" if path == "/" else path.removeprefix("/web/")
            if (path == "/" or path.startswith("/web/")) and re.fullmatch(r"[a-zA-Z0-9_-]+\.(?:html|css|js|svg|ico|png)", static):
                mime = {"html": "text/html; charset=utf-8", "css": "text/css; charset=utf-8",
                        "js": "text/javascript; charset=utf-8", "svg": "image/svg+xml",
                        "png": "image/png", "ico": "image/x-icon"}[static.rsplit(".", 1)[1]]
                return self._file(self.server.web_root / static, mime)
        raise RequestError(404, "未找到该入口")


def make_server(data_dir, port=8765, *, processor=process_job, web_root=WEB_ROOT):
    store = JobStore(data_dir, processor)
    try:
        return SurveyHTTPServer(("127.0.0.1", port), store, web_root)
    except BaseException:
        store.close()
        raise


def _workbench_listening(port):
    connection = HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        return response.status == 200 and response.getheader("Server", "").strip() == SurveyHandler.server_version
    except (OSError, HTTPException):
        return False
    finally:
        connection.close()


def main(argv=None):
    cli = argparse.ArgumentParser(description="启动独立综述阅读工作台")
    cli.add_argument("--port", type=int, default=8765)
    cli.add_argument("--data-dir", type=Path, default=ROOT / "workspace", help="保存工作台任务的本地目录")
    cli.add_argument("--open-browser", action="store_true", help="在浏览器中打开本地工作台")
    args = cli.parse_args(argv)
    if args.open_browser:
        import webbrowser
        if args.data_dir.resolve() == ROOT / "workspace" and _workbench_listening(args.port):
            webbrowser.open(f"http://127.0.0.1:{args.port}/")
            return
    load_service_env()
    try:
        with make_server(args.data_dir, args.port) as server:
            print(f"综述精读工作台 http://127.0.0.1:{server.server_port}", flush=True)
            if args.open_browser:
                webbrowser.open(f"http://127.0.0.1:{server.server_port}/")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    except (OSError, ValueError) as error:
        cli.exit(1, f"无法启动工作台：{error}\n")


if __name__ == "__main__":
    main()
