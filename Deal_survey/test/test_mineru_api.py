from io import BytesIO
import json
from pathlib import Path
import socket
import ssl
import tempfile
import time
import unittest
from unittest.mock import patch

from deal_survey import mineru_api, mineru_pdf

from .test_mineru_pdf import result_zip, write_pdf


class SimulatedTransport:
    def __init__(self):
        self.calls = []
        self.download = "https://objects.example/down?s=redacted"
        self.upload = "https://objects.example/up?s=redacted"
        self.data_id = None
        self.poll_rows = None

    def request(self, method, url, *, headers, body, deadline, max_bytes):
        self.calls.append((method, url, headers, body))
        if method == "POST":
            payload = json.loads(body)
            self.data_id = payload["files"][0]["data_id"]
            data = {"batch_id": "case_1", "file_urls": [self.upload]}
        elif url == self.upload:
            return b""
        elif url == self.download:
            return result_zip()
        else:
            rows = self.poll_rows
            if rows is None:
                rows = [{"data_id": self.data_id, "state": "done", "full_zip_url": self.download}]
            data = {"extract_result": rows}
        return json.dumps({"code": 0, "data": data}).encode()


class WireSocket:
    """One TLS stream after the mocked connect, using Python's real HTTP codec."""

    def __init__(self, response):
        self.response = response
        self.sent = bytearray()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def settimeout(self, seconds):
        pass

    def sendall(self, data):
        self.sent.extend(data)

    def makefile(self, mode):
        return BytesIO(self.response)

    def shutdown(self, how):
        pass


class MinerUAPITests(unittest.TestCase):
    def test_v4_protocol_from_pdf_to_result_with_fake_transport(self):
        transport = SimulatedTransport()
        client = mineru_api.MinerUAPI("synthetic-token", model="pipeline", transport=transport)
        with tempfile.TemporaryDirectory() as temp:
            pdf = Path(temp) / "source.pdf"
            write_pdf(pdf, 2)
            receipt = mineru_pdf.parse_pdf(pdf, Path(temp) / "run", model="pipeline", provider=client)
            blocks, meta = mineru_pdf.load_parse(pdf, receipt["result_zip"])
            self.assertEqual(blocks[0]["text"], "body")
            self.assertEqual(meta["batch_id"], "case_1")
            self.assertEqual([c[:2] for c in transport.calls], [
                ("POST", mineru_api.API + "/file-urls/batch"), ("PUT", transport.upload),
                ("GET", mineru_api.API + "/extract-results/batch/case_1"), ("GET", transport.download)])
            self.assertEqual(transport.calls[1][3], pdf.read_bytes())
            payload = json.loads(transport.calls[0][3])
            self.assertEqual(payload["model_version"], "pipeline")
            self.assertTrue(payload["enable_table"] and payload["enable_formula"])
            self.assertEqual(payload["files"][0]["page_ranges"], "1-2")
            self.assertEqual(payload["files"][0]["data_id"], receipt["source_sha256"])
            for index, (_, _, headers, _) in enumerate(transport.calls):
                self.assertEqual("Authorization" in headers, index in (0, 2))

    def test_poll_matches_identity_and_rejects_ambiguous_rows(self):
        transport = SimulatedTransport()
        client = mineru_api.MinerUAPI("fake", transport=transport)
        for rows in ([{"data_id": "other", "state": "done"}], [{"data_id": "mine"}, {"data_id": "mine"}]):
            transport.poll_rows = rows
            with self.assertRaisesRegex(ValueError, "identity_mismatch"):
                client.poll("case_1", data_id="mine", deadline=time.monotonic() + 10)
        transport.poll_rows = []
        self.assertEqual(client.poll("case_1", data_id="mine", deadline=time.monotonic() + 10), {"state": "pending"})

    def test_object_put_redirect_keeps_pdf_and_never_forwards_authorization(self):
        transport = mineru_api.DirectHTTPS()
        self.assertEqual(transport.context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(transport.context.check_hostname)
        redirect = WireSocket(b"HTTP/1.1 307 Temporary Redirect\r\nLocation: https://other.example/b?s=x\r\n\r\n")
        success = WireSocket(b"HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: 5\r\n\r\nhello")
        with patch.object(transport, "_connect", side_effect=[redirect, success]):
            reply = transport.request("PUT", "https://objects.example/a?s=y", headers={}, body=b"%PDF-test",
                                      deadline=time.monotonic() + 10, max_bytes=16)
        self.assertEqual(reply, b"hello")
        for stream, host in ((redirect, b"objects.example"), (success, b"other.example")):
            self.assertIn(b"Host: " + host + b"\r\n", stream.sent)
            self.assertTrue(stream.sent.endswith(b"%PDF-test"))
            self.assertNotIn(b"Authorization", stream.sent)

    def test_unsafe_or_expired_requests_never_reach_objects_with_credentials(self):
        transport = mineru_api.DirectHTTPS()
        with patch.object(transport, "_once", return_value=(307, "https://objects.example/x", b"")) as once:
            for url in ("https://objects.example/x", "https://mineru.net/a", "https://127.0.0.1/a"):
                with self.assertRaises(ValueError):
                    transport.request("GET", url, headers={"authorization": "Bearer fake"}, body=None,
                                      deadline=time.monotonic() + 10, max_bytes=16)
            once.assert_not_called()
            with self.assertRaisesRegex(ValueError, "redirect_rejected"):
                transport.request("GET", mineru_api.API + "/extract-results/batch/one",
                                  headers={"Authorization": "Bearer fake"}, body=None,
                                  deadline=time.monotonic() + 10, max_bytes=16)
            self.assertEqual(once.call_count, 1)
        mixed_dns = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443)) for ip in ("8.8.8.8", "127.0.0.1")]
        with patch.object(socket, "getaddrinfo", return_value=mixed_dns), patch.object(socket, "socket") as tcp:
            with self.assertRaisesRegex(ValueError, "unsafe_dns_destination"):
                transport.request("GET", "https://objects.example/test", headers={}, body=None,
                                  deadline=time.monotonic() + 10, max_bytes=16)
            tcp.assert_not_called()
        client = mineru_api.MinerUAPI("fake", transport=SimulatedTransport())
        with self.assertRaises(TimeoutError):
            client.result("https://objects.example/a", deadline=time.monotonic() - 1)
        self.assertEqual(client.transport.calls, [])


if __name__ == "__main__":
    unittest.main()
