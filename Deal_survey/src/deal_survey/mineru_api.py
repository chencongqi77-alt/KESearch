"""Standalone MinerU v4 calls adapted from Test01/work_tool/mineru_client.py and mineru_transport.py."""

from __future__ import annotations

import http.client
import ipaddress
import json
import queue
import re
import socket
import ssl
import threading
import time
from urllib.parse import urljoin, urlsplit


API = "https://mineru.net/api/v4"
MAX_ZIP_BYTES = 200 * 1024 * 1024
_DNS_SLOTS = threading.BoundedSemaphore(4)
_BATCH = re.compile(r"[A-Za-z0-9_-]{1,150}")


class MinerUError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _remaining(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("MinerU 请求超时")
    return remaining


def _public(address):
    value = ipaddress.ip_address(address)
    return value.is_global and not value.is_multicast


def _destination(url):
    try:
        if (not isinstance(url, str) or len(url) > 16384 or "\\" in url
                or any(ord(char) < 33 or ord(char) == 127 for char in url)):
            raise ValueError()
        parsed = urlsplit(url)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.port not in {None, 443}
                or parsed.username is not None or parsed.password is not None or parsed.fragment):
            raise ValueError()
        try:
            literal = ipaddress.ip_address(host)
        except ValueError:
            if ("." not in host or host.rstrip(".").endswith((".local", ".localhost", ".internal"))
                    or not re.fullmatch(r"[a-z0-9.-]{1,253}", host)):
                raise ValueError()
        else:
            if not _public(literal):
                raise ValueError()
        return parsed
    except (ValueError, UnicodeError):
        raise MinerUError("unsafe_https_destination") from None


def _resolve(host, deadline):
    if not _DNS_SLOTS.acquire(timeout=_remaining(deadline)):
        raise TimeoutError("MinerU DNS 超时")
    answers = queue.Queue(maxsize=1)

    def resolve():
        try:
            rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            answers.put([(family, target) for family, _, _, _, target in rows])
        except OSError:
            answers.put([])
        finally:
            _DNS_SLOTS.release()

    threading.Thread(target=resolve, daemon=True).start()
    try:
        addresses = answers.get(timeout=min(10, _remaining(deadline)))
    except queue.Empty:
        raise TimeoutError("MinerU DNS 超时") from None
    if not addresses:
        raise MinerUError("dns_failed")
    if any(not _public(target[0]) for _, target in addresses):
        raise MinerUError("unsafe_dns_destination")
    return list(dict.fromkeys(addresses))[:3]


def _interrupt(sock):
    # A hard deadline also bounds slow HTTP header/body streams.
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass


class DirectHTTPS:
    """Connect to checked DNS answers directly, keeping TLS hostname verification."""

    def __init__(self):
        self.context = ssl.create_default_context()

    def _connect(self, host, deadline):
        for family, address in _resolve(host, deadline):
            try:
                with socket.socket(family, socket.SOCK_STREAM) as raw:
                    raw.settimeout(min(15, _remaining(deadline)))
                    raw.connect(address)
                    raw.settimeout(min(15, _remaining(deadline)))
                    return self.context.wrap_socket(raw, server_hostname=host)
            except ssl.SSLCertVerificationError:
                raise MinerUError("tls_verification_failed") from None
            except OSError:
                # Trying another public address is safe before any HTTP request bytes.
                continue
        _remaining(deadline)
        raise MinerUError("connection_failed")

    def _once(self, method, parsed, headers, body, deadline, max_bytes):
        with self._connect(parsed.hostname, deadline) as sock:
            sock.settimeout(_remaining(deadline))
            timer = threading.Timer(_remaining(deadline), _interrupt, args=(sock,))
            timer.daemon = True
            timer.start()
            try:
                connection = http.client.HTTPSConnection(parsed.hostname, context=self.context)
                connection.sock = sock
                path = parsed.path or "/"
                if parsed.query:
                    path += "?" + parsed.query
                connection.request(method, path, body=body, headers=headers)
                # Own the TLS socket until the full body has been read, including Connection: close.
                with http.client.HTTPResponse(sock, method=method) as response:
                    response.begin()
                    if 300 <= response.status < 400:
                        return response.status, response.getheader("Location"), b""
                    if not 200 <= response.status < 300:
                        return response.status, None, b""
                    length = response.length
                    if length is not None and length > max_bytes:
                        raise MinerUError("response_too_large")
                    data = response.read(max_bytes + 1)
                    if len(data) > max_bytes:
                        raise MinerUError("response_too_large")
                    if length is not None and len(data) != length:
                        raise MinerUError("incomplete_response")
                    _remaining(deadline)
                    return response.status, None, data
            finally:
                timer.cancel()

    def request(self, method, url, *, headers, body, deadline, max_bytes):
        authenticated = any(key.lower() == "authorization" for key in headers)
        if method not in {"GET", "POST", "PUT"}:
            raise MinerUError("invalid_request_method")
        for _ in range(5):
            parsed = _destination(url)
            is_api = (parsed.hostname == "mineru.net" and not parsed.query and
                      ((method == "POST" and parsed.path == "/api/v4/file-urls/batch") or
                       (method == "GET" and re.fullmatch(r"/api/v4/extract-results/batch/[A-Za-z0-9_-]{1,150}", parsed.path))))
            if (authenticated or method == "POST") and not (authenticated and is_api):
                raise MinerUError("authorization_destination_rejected")
            try:
                status, location, data = self._once(method, parsed, headers, body, deadline, max_bytes)
            except (OSError, http.client.HTTPException, UnicodeError):
                _remaining(deadline)
                raise MinerUError("network_or_tls_error") from None
            if 200 <= status < 300:
                return data
            if status not in {301, 302, 303, 307, 308}:
                code = {401: "unauthorized", 403: "forbidden", 429: "rate_limited"}.get(status, "http_request_failed")
                raise MinerUError(code)
            if authenticated or not location or (method == "PUT" and status not in {307, 308}):
                raise MinerUError("redirect_rejected")
            url = urljoin(url, location)
        raise MinerUError("redirect_limit")


class MinerUAPI:
    def __init__(self, token, *, model="vlm", transport=None):
        if not token or any(char.isspace() or not char.isprintable() for char in token):
            raise MinerUError("invalid_api_token")
        if model not in {"vlm", "pipeline"}:
            raise MinerUError("invalid_model")
        self._token = token
        self.model = model
        self.transport = transport or DirectHTTPS()

    def _request(self, method, url, *, deadline, authenticated=False, body=None, max_bytes=4 * 1024 * 1024):
        _destination(url)
        _remaining(deadline)
        headers = {"User-Agent": "KESearch-Deal-Survey/1.0", "Connection": "close", "Accept-Encoding": "identity"}
        if authenticated:
            headers.update({"Authorization": "Bearer " + self._token, "Content-Type": "application/json"})
        raw = self.transport.request(method, url, headers=headers, body=body,
                                     deadline=min(deadline, time.monotonic() + 120), max_bytes=max_bytes)
        if len(raw) > max_bytes:
            raise MinerUError("response_too_large")
        if not authenticated:
            return raw
        try:
            reply = json.loads(raw)
        except (ValueError, UnicodeError):
            raise MinerUError("invalid_api_json") from None
        if (not isinstance(reply, dict) or type(reply.get("code")) is not int or reply["code"] != 0
                or not isinstance(reply.get("data"), dict)):
            raise MinerUError("provider_rejected")
        return reply["data"]

    def submit(self, data_id, *, deadline, max_pages):
        if type(max_pages) is not int or not 1 <= max_pages <= 200 or not re.fullmatch(r"[0-9a-f]{64}", data_id):
            raise MinerUError("invalid_submission_input")
        payload = {"files": [{"name": data_id[:32] + ".pdf", "data_id": data_id, "page_ranges": f"1-{max_pages}"}],
                   "model_version": self.model, "enable_formula": True, "enable_table": True}
        data = self._request("POST", API + "/file-urls/batch", deadline=deadline, authenticated=True,
                             body=json.dumps(payload).encode("utf-8"))
        batch, urls = data.get("batch_id"), data.get("file_urls")
        if not isinstance(batch, str) or not _BATCH.fullmatch(batch) or not isinstance(urls, list) or len(urls) != 1:
            raise MinerUError("invalid_submission_response")
        _destination(urls[0])
        return {"batch_id": batch, "upload_url": urls[0]}

    def upload(self, url, raw, *, deadline):
        self._request("PUT", url, body=raw, deadline=deadline, max_bytes=1024 * 1024)

    def poll(self, batch_id, *, data_id, deadline):
        if not isinstance(batch_id, str) or not _BATCH.fullmatch(batch_id):
            raise MinerUError("invalid_batch_id")
        data = self._request("GET", API + "/extract-results/batch/" + batch_id, deadline=deadline, authenticated=True)
        rows = data.get("extract_result")
        if not isinstance(rows, list):
            raise MinerUError("invalid_poll_response")
        if not rows:
            return {"state": "pending"}
        if len(rows) == 1 and isinstance(rows[0], dict) and rows[0].get("data_id") is None:
            return rows[0]
        matches = [row for row in rows if isinstance(row, dict) and row.get("data_id") == data_id]
        if len(matches) != 1:
            raise MinerUError("parse_result_identity_mismatch")
        return matches[0]

    def result(self, url, *, deadline):
        return self._request("GET", url, deadline=deadline, max_bytes=MAX_ZIP_BYTES)
