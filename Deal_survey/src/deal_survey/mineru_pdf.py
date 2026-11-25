"""Submit whole PDFs to MinerU and read v1 content blocks from bound result ZIPs."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import time
from zipfile import BadZipFile, ZipFile

from .mineru_api import MAX_ZIP_BYTES, MinerUAPI

MAX_PDF_BYTES = 200 * 1024 * 1024
MAX_UNPACKED_BYTES = 512 * 1024 * 1024
MAX_ZIP_FILES = 5000


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect_pdf(path):
    """Inspect and fingerprint the exact upload bytes, adapted from Test01/work_tool/mineru_client.py."""
    from pypdf import PdfReader

    source = Path(path)
    if source.suffix.lower() != ".pdf" or not source.is_file() or source.stat().st_size > MAX_PDF_BYTES:
        raise ValueError("输入不是可读取的 PDF 或超出 200 MiB 限制")
    with source.open("rb") as handle:
        raw = handle.read(MAX_PDF_BYTES + 1)
    if len(raw) > MAX_PDF_BYTES or not raw.startswith(b"%PDF-"):
        raise ValueError("PDF 文件头或大小无效")
    try:
        pages = len(PdfReader(io.BytesIO(raw), strict=False).pages)
    except Exception:
        raise ValueError("无法读取输入 PDF 的页数") from None
    if not pages:
        raise ValueError("输入 PDF 没有页")
    return raw, {"source_sha256": _digest(raw), "pdf_pages": pages}


def _atomic_bytes(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _write_json(path, value):
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


@contextmanager
def _run_lock(run):
    run.mkdir(parents=True, exist_ok=True)
    path = run / ".mineru.lock"
    if not path.exists() and any(run.iterdir()):
        raise ValueError("请选择新的云运行目录")
    with path.open("a+b") as handle:
        try:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("MinerU 运行目录正在使用") from error
        yield


def _member(members, predicate, label, *, required=False):
    matches = [item for item in members if predicate(PurePosixPath(item.filename).name.casefold())]
    if len(matches) > 1 or (required and not matches):
        raise ValueError(f"MinerU ZIP 中的{label}必须唯一，实际找到 {len(matches)} 个")
    return matches[0] if matches else None


def _check_receipt(receipt, source, zip_sha):
    if (not isinstance(receipt, dict) or receipt.get("status") != "complete"
            or receipt.get("source_sha256") != source["source_sha256"]
            or receipt.get("zip_sha256") != zip_sha):
        raise ValueError("MinerU 回执与输入 PDF 或 ZIP 指纹不匹配")
    if (type(receipt.get("pdf_pages")) is not int or receipt["pdf_pages"] != source["pdf_pages"]
            or type(receipt.get("requested_pages")) is not int or receipt["requested_pages"] != source["pdf_pages"]
            or receipt.get("full_document_requested") is not True):
        raise ValueError("MinerU 回执未确认请求覆盖完整 PDF")
    provider_pages = receipt.get("provider_total_pages")
    if provider_pages is not None and (type(provider_pages) is not int or provider_pages != source["pdf_pages"]):
        raise ValueError("MinerU 提供方记录的页数与输入 PDF 不一致")


def _read_package(source, raw, receipt):
    zip_sha = _digest(raw)
    if receipt is not None:
        _check_receipt(receipt, source, zip_sha)
    try:
        with ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            if (len(members) > MAX_ZIP_FILES or sum(i.file_size for i in members) > MAX_UNPACKED_BYTES
                    or len(raw) > MAX_ZIP_BYTES):
                raise ValueError("MinerU ZIP 超过大小或成员数量限制")
            files = [item for item in members if not item.is_dir()]
            content = _member(files, lambda n: n == "content_list.json" or n.endswith("_content_list.json"),
                              "v1 content_list", required=True)
            origin = _member(files, lambda n: n == "origin.pdf" or n.endswith("_origin.pdf"), "提供方 PDF")
            origin_sha = _digest(archive.read(origin)) if origin else None
            same_origin = None if origin is None else origin_sha == source["source_sha256"]
            if not same_origin and receipt is None:
                raise ValueError("ZIP 未包含同字节原件，需提供同时绑定该 PDF 和 ZIP 的完整解析回执")
            blocks = json.loads(archive.read(content).decode("utf-8-sig"))
            if not isinstance(blocks, list) or not blocks or not all(isinstance(item, dict) for item in blocks):
                raise ValueError("MinerU v1 content_list 应为非空的对象列表")
            markdown = _member(files, lambda n: n in {"full.md", "fulltext.md"}, "全文 Markdown")
            if markdown is None:
                markdown = _member(files, lambda n: n.endswith(".md"), "Markdown")
            markdown_raw = archive.read(markdown) if markdown else None
    except (BadZipFile, NotImplementedError, RuntimeError) as error:
        raise ValueError("无法读取 MinerU ZIP 成员") from error
    meta = {
        "source_sha256": source["source_sha256"], "pdf_pages": source["pdf_pages"], "zip_sha256": zip_sha,
        "content_list_member": content.filename, "markdown_member": markdown.filename if markdown else None,
        "provider_origin_sha256": origin_sha, "origin_bytes_equal": same_origin,
        "identity_basis": "embedded_origin_sha256" if same_origin else "receipt_source_and_zip_sha256",
        "page_scope": "full_document_requested" if receipt is not None else "unverified",
        "requested_pages": receipt.get("requested_pages") if receipt else None,
        "provider_total_pages": receipt.get("provider_total_pages") if receipt else None,
        "batch_id": receipt.get("batch_id") if receipt else None,
    }
    return blocks, meta, markdown_raw


def load_parse(pdf_path, archive_path, *, receipt_path=None):
    """Read original v1 blocks, checking an adjacent Test01/new result.json when present."""
    source = inspect_pdf(pdf_path)[1]
    archive = Path(archive_path)
    if archive.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError("MinerU ZIP 超过大小限制")
    receipt_file = Path(receipt_path) if receipt_path is not None else archive.with_name("result.json")
    receipt = None
    if receipt_path is not None or receipt_file.exists():
        receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
        if not isinstance(receipt, dict):
            raise ValueError("MinerU 回执必须为 JSON 对象")
    blocks, meta, _ = _read_package(source, archive.read_bytes(), receipt)
    return blocks, meta


def _live_provider(model):
    token = os.environ.get("KET_MINERU_API_TOKEN", "").strip()
    if not token:
        raise ValueError("云端解析需要进程环境变量 KET_MINERU_API_TOKEN")
    return MinerUAPI(token, model=model)


def _call_remote(method, *args, **kwargs):
    # A transport exception may include a signed request URL or authorization headers.
    try:
        return method(*args, **kwargs)
    except TimeoutError:
        raise TimeoutError("MinerU 请求超时") from None
    except Exception as error:
        code = getattr(error, "code", None)
        if not isinstance(code, str) or not re.fullmatch(r"[a-z_]{1,64}", code):
            code = "provider_error"
        raise ValueError(f"MinerU 请求失败（{code}）") from None


def _fetch(provider, source_raw, state, state_path, archive, deadline):
    data_id = state["source_sha256"]
    if not state.get("batch_id"):
        if state["phase"] != "prepared":
            raise ValueError("上次云提交结果不明，无法安全地再次提交")
        state["phase"] = "submitting"
        _write_json(state_path, state)
        job = _call_remote(provider.submit, data_id, deadline=deadline, max_pages=state["pdf_pages"])
        if not isinstance(job, dict) or not re.fullmatch(r"[A-Za-z0-9_-]{1,150}", str(job.get("batch_id") or "")):
            raise ValueError("MinerU 云提交回执缺少有效批次号")
        state.update(phase="submitted", batch_id=job["batch_id"])
        _write_json(state_path, state)
        if not isinstance(job.get("upload_url"), str):
            raise ValueError("MinerU 批次缺少签名上传地址")
        _call_remote(provider.upload, job["upload_url"], source_raw, deadline=deadline)
        state["phase"] = "uploaded"
        _write_json(state_path, state)
    if state["phase"] == "failed":
        raise ValueError("该云批次已失败")
    while time.monotonic() < deadline:
        row = _call_remote(provider.poll, state["batch_id"], data_id=data_id, deadline=deadline)
        status = row.get("state") if isinstance(row, dict) else None
        if status not in ("done", "failed", "pending", "running", "waiting-file", "converting"):
            raise ValueError("MinerU 云批次状态无效")
        progress = row.get("extract_progress")
        pages = progress.get("total_pages") if isinstance(progress, dict) else None
        if pages is not None:
            if type(pages) is not int or pages < 0:
                raise ValueError("MinerU 云批次页数无效")
            if pages != state.get("provider_total_pages"):
                state["provider_total_pages"] = pages
                _write_json(state_path, state)
        if status == "failed":
            state["phase"] = "failed"
            _write_json(state_path, state)
            raise ValueError("MinerU 云批次解析失败")
        if status == "waiting-file" and state["phase"] == "submitted":
            raise ValueError("已有云批次仍等待文件，原签名上传地址未保存，不能自动重提")
        if status == "done":
            if not isinstance(row.get("full_zip_url"), str):
                raise ValueError("MinerU 完成的批次缺少签名下载地址")
            package = _call_remote(provider.result, row["full_zip_url"], deadline=deadline)
            if len(package) > MAX_ZIP_BYTES:
                raise ValueError("MinerU ZIP 超过大小限制")
            state.update(phase="received", zip_sha256=_digest(package))
            _write_json(state_path, state)
            _atomic_bytes(archive, package)
            return
        time.sleep(max(0, min(5, deadline - time.monotonic())))
    raise TimeoutError("等待 MinerU 超时，可在同一目录恢复已知批次")


def parse_pdf(pdf_path, run_dir, *, model="vlm", max_wait_seconds=900, provider=None):
    """Parse one entire PDF into an exclusive cloud directory; return its verified receipt."""
    if model not in {"vlm", "pipeline"} or not math.isfinite(max_wait_seconds) or max_wait_seconds <= 0:
        raise ValueError("MinerU 模型或等待时间无效")
    source_raw, source = inspect_pdf(pdf_path)
    if source["pdf_pages"] > 200:
        raise ValueError("当前整篇上传支持最多 200 页")
    run = Path(run_dir).resolve()
    state_path, archive, result = run / "state.json", run / "result.zip", run / "result.json"
    identity = {"schema": "deal-survey-mineru-v1", "model": model, "source_sha256": source["source_sha256"],
                "pdf_pages": source["pdf_pages"]}
    with _run_lock(run):
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if any(state.get(key) != value for key, value in identity.items()):
                raise ValueError("云运行目录与输入 PDF、模型或状态格式不匹配")
        else:
            if any(item.name != ".mineru.lock" for item in run.iterdir()):
                raise ValueError("请选择新的云运行目录")
            state = {**identity, "phase": "prepared"}
            _write_json(state_path, state)
        if not archive.is_file():
            if result.exists():
                raise ValueError("已完成云批次的原始 ZIP 缺失")
            client = provider if provider is not None else _live_provider(model)
            _fetch(client, source_raw, state, state_path, archive, time.monotonic() + max_wait_seconds)
        receipt = {"status": "complete", "source_sha256": source["source_sha256"], "pdf_pages": source["pdf_pages"],
                   "requested_pages": source["pdf_pages"], "full_document_requested": True,
                   "provider_total_pages": state.get("provider_total_pages"), "batch_id": state["batch_id"],
                   "zip_sha256": state["zip_sha256"], "model": model}
        if archive.stat().st_size > MAX_ZIP_BYTES:
            raise ValueError("MinerU ZIP 超过大小限制")
        _, meta, markdown = _read_package(source, archive.read_bytes(), receipt)
        markdown_path = run / "full.md"
        receipt.update(result_zip=str(archive), markdown_path=str(markdown_path) if markdown is not None else None,
                       content_list_member=meta["content_list_member"])
        if result.exists():
            saved = json.loads(result.read_text(encoding="utf-8"))
            _check_receipt(saved, source, receipt["zip_sha256"])
            if saved.get("batch_id") != state["batch_id"] or saved.get("model") != model:
                raise ValueError("已完成批次的回执与运行状态不匹配")
            if markdown is not None and markdown_path.read_bytes() != markdown:
                raise ValueError("已保存的 Markdown 与原始 ZIP 成员不匹配")
            return receipt
        if markdown is not None:
            _atomic_bytes(markdown_path, markdown)
        _write_json(result, receipt)
        return receipt
