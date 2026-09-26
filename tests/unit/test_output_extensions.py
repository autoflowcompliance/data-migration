"""Signed deliverables, webhooks and push destinations (Layer 8)."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from app_files.output import (
    EmailDestination,
    FileDestination,
    GoogleSheetsDestination,
    S3Destination,
    SFTPDestination,
    SignatureError,
    Webhook,
    WebhookDispatcher,
    notify_completion,
    push,
    push_file,
    read_manifest,
    sign_bytes,
    sign_directory,
    sign_file,
    verify_file,
    verify_or_raise,
    write_manifest,
)

KEY = "test-signing-key"


class TestSignedDeliverables:
    def test_sign_and_verify(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("a,b\n1,2\n")
        manifest = sign_file(target, KEY)
        assert verify_file(target, manifest, KEY)

    def test_a_tampered_file_fails_verification(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("a,b\n1,2\n")
        manifest = sign_file(target, KEY)
        target.write_text("a,b\n1,999\n")
        assert not verify_file(target, manifest, KEY)

    def test_verify_or_raise_explains_the_failure(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("a,b\n1,2\n")
        manifest = sign_file(target, KEY)
        target.write_text("a,b\n1,999\n")
        with pytest.raises(SignatureError, match="changed after signing"):
            verify_or_raise(target, manifest, KEY)

    def test_wrong_key_fails(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("a,b\n1,2\n")
        manifest = sign_file(target, KEY)
        assert not verify_file(target, manifest, "another-key")

    def test_missing_file_fails_rather_than_raising(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("x")
        manifest = sign_file(target, KEY)
        target.unlink()
        assert not verify_file(target, manifest, KEY)

    def test_verify_or_raise_on_missing_file(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("x")
        manifest = sign_file(target, KEY)
        target.unlink()
        with pytest.raises(SignatureError, match="missing"):
            verify_or_raise(target, manifest, KEY)

    def test_signing_a_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            sign_file(tmp_path / "nope.csv", KEY)

    def test_manifest_round_trips_through_disk(self, tmp_path):
        target = tmp_path / "out.csv"
        target.write_text("a,b\n1,2\n")
        manifest = sign_file(target, KEY)
        sidecar = write_manifest(manifest, tmp_path / "out.manifest.json")
        restored = read_manifest(sidecar)
        assert restored.sha256 == manifest.sha256
        assert verify_file(target, restored, KEY)

    def test_manifest_from_dict_rejects_incomplete_input(self):
        from app_files.output import SignatureManifest

        with pytest.raises(SignatureError, match="missing"):
            SignatureManifest.from_dict({"filename": "x"})

    def test_sign_bytes_matches_the_file_it_would_write(self):
        data = b"col\n1\n"
        manifest = sign_bytes(data, "x.csv", KEY)
        assert manifest.size == len(data)
        assert manifest.filename == "x.csv"

    def test_sign_directory_skips_its_own_manifests(self, tmp_path):
        (tmp_path / "a.csv").write_text("1")
        (tmp_path / "b.json").write_text("{}")
        (tmp_path / "a.csv.manifest.json").write_text("{}")
        bundle = sign_directory(tmp_path, KEY)
        assert {m.filename for m in bundle.manifests} == {"a.csv", "b.json"}

    def test_bundle_verify_all_reports_per_file(self, tmp_path):
        (tmp_path / "a.csv").write_text("1")
        (tmp_path / "b.csv").write_text("2")
        bundle = sign_directory(tmp_path, KEY)
        assert all(bundle.verify_all(tmp_path, KEY).values())
        (tmp_path / "b.csv").write_text("tampered")
        results = bundle.verify_all(tmp_path, KEY)
        assert results["a.csv"] and not results["b.csv"]


class _Listener:
    """A real HTTP listener, because a mocked transport proves nothing about HTTP."""

    def __init__(self):
        self.received: list[dict] = []
        received = self.received

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                received.append(
                    {
                        "path": self.path,
                        "body": json.loads(self.rfile.read(length)),
                        "signature": self.headers.get("X-DataFlow-Signature"),
                    }
                )
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):  # silence the test log
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/hook"

    def stop(self) -> None:
        self.server.shutdown()


@pytest.fixture
def listener():
    server = _Listener()
    yield server
    server.stop()


class TestWebhooks:
    def test_payload_arrives_with_correct_fields(self, listener):
        dispatcher = WebhookDispatcher([Webhook(listener.url)])
        results = notify_completion(
            "run-1",
            {"quality_score": 97.5, "rows_in": 100, "rows_out": 98},
            dispatcher,
            output_location="/tmp/out.csv",
            source="crm",
        )
        assert results[0].delivered
        body = listener.received[0]["body"]
        assert body["event"] == "run.completed"
        assert body["run_id"] == "run-1"
        assert body["quality_score"] == 97.5
        assert body["output_location"] == "/tmp/out.csv"

    def test_failure_fires_the_failed_event(self, listener):
        dispatcher = WebhookDispatcher([Webhook(listener.url)])
        notify_completion("run-2", {}, dispatcher, error="boom")
        body = listener.received[0]["body"]
        assert body["event"] == "run.failed"
        assert body["status"] == "failed"
        assert body["error"] == "boom"

    def test_signature_is_sent_when_a_secret_is_set(self, listener):
        dispatcher = WebhookDispatcher([Webhook(listener.url, secret="whsec")])
        notify_completion("run-3", {}, dispatcher)
        assert listener.received[0]["signature"].startswith("sha256=")

    def test_subscriber_only_gets_subscribed_events(self):
        dispatcher = WebhookDispatcher(
            [Webhook("http://unused/hook", events=("run.failed",))],
            transport=lambda *args: 200,
        )
        assert notify_completion("r", {}, dispatcher) == []
        delivered = notify_completion("r", {}, dispatcher, error="x")
        assert delivered and delivered[0].delivered

    def test_a_dead_endpoint_does_not_raise(self):
        dispatcher = WebhookDispatcher([Webhook("http://127.0.0.1:1/hook", timeout=0.2)])
        results = notify_completion("r", {}, dispatcher)
        assert results and not results[0].delivered
        assert results[0].error

    def test_non_2xx_is_reported_as_a_failure(self):
        dispatcher = WebhookDispatcher(
            [Webhook("http://x/hook")], transport=lambda *args: 500
        )
        result = notify_completion("r", {}, dispatcher)[0]
        assert not result.delivered
        assert result.status_code == 500
        assert "HTTP 500" in (result.error or "")

    def test_payload_is_json_safe(self):
        import json as _json

        from app_files.output import WebhookPayload

        payload = WebhookPayload("run.completed", "r", "completed", extra={"n": 1})
        _json.dumps(payload.as_dict())


class TestDestinations:
    def test_file_destination_writes_the_bytes(self, tmp_path):
        receipt = FileDestination(tmp_path / "out").deliver(b"payload", "f.bin")
        assert receipt.delivered
        assert (tmp_path / "out" / "f.bin").read_bytes() == b"payload"

    def test_push_returns_a_receipt_per_destination(self, tmp_path):
        receipts = push(
            b"x", "f.bin", [FileDestination(tmp_path / "a"), FileDestination(tmp_path / "b")]
        )
        assert len(receipts) == 2
        assert all(receipt.delivered for receipt in receipts)

    def test_push_file_reads_from_disk(self, tmp_path):
        source = tmp_path / "src.bin"
        source.write_bytes(b"from-disk")
        receipts = push_file(source, [FileDestination(tmp_path / "dest")])
        assert receipts[0].delivered
        assert (tmp_path / "dest" / "src.bin").read_bytes() == b"from-disk"

    def test_s3_uses_prefix_and_reports_the_location(self):
        calls = []

        class FakeClient:
            def put_object(self, **kwargs):
                calls.append(kwargs)

        destination = S3Destination("bucket", "pre/", client=FakeClient())
        receipt = destination.deliver(b"data", "f.csv")
        assert receipt.delivered
        assert calls[0]["Key"] == "pre/f.csv"
        assert receipt.detail == "s3://bucket/pre/f.csv"

    def test_s3_failure_is_a_receipt_not_an_exception(self):
        class BrokenClient:
            def put_object(self, **kwargs):
                raise RuntimeError("no credentials")

        receipt = S3Destination("bucket", client=BrokenClient()).deliver(b"d", "f")
        assert not receipt.delivered
        assert "no credentials" in (receipt.detail or "")

    def test_sftp_without_a_transport_says_so(self):
        receipt = SFTPDestination("host", "/dir").deliver(b"d", "f")
        assert not receipt.delivered
        assert "No SFTP transport" in (receipt.detail or "")

    def test_sftp_uses_the_injected_transport(self):
        calls = []
        destination = SFTPDestination(
            "host", "/dir", username="u",
            transport=lambda *args: calls.append(args),
        )
        receipt = destination.deliver(b"d", "f.csv")
        assert receipt.delivered
        assert calls[0][1] == "/dir/f.csv"

    def test_sheets_without_a_transport_says_so(self):
        receipt = GoogleSheetsDestination("http://sheet").deliver(b"d", "f")
        assert not receipt.delivered
        assert "No Sheets transport" in (receipt.detail or "")

    def test_sheets_reports_an_http_failure(self):
        destination = GoogleSheetsDestination(
            "http://sheet", transport=lambda *args: 403
        )
        receipt = destination.deliver(b"d", "f")
        assert not receipt.delivered
        assert receipt.detail == "HTTP 403"

    def test_email_builds_a_message_with_an_attachment(self):
        destination = EmailDestination(["a@x.com"], sender="me@x.com")
        message = destination.build_message(b"data", "out.csv")
        assert message["To"] == "a@x.com"
        assert any(part.get_filename() == "out.csv" for part in message.iter_attachments())

    def test_email_uses_the_injected_smtp_factory(self):
        sent = []

        class FakeSMTP:
            def __init__(self, host, port):
                sent.append((host, port))

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def send_message(self, message):
                sent.append(message)

        destination = EmailDestination(
            ["a@x.com"], host="mail", port=2525, smtp_factory=FakeSMTP
        )
        receipt = destination.deliver(b"data", "out.csv")
        assert receipt.delivered
        assert sent[0] == ("mail", 2525)

    def test_email_failure_is_a_receipt(self):
        class BrokenSMTP:
            def __init__(self, host, port):
                raise OSError("connection refused")

        destination = EmailDestination(["a@x.com"], smtp_factory=BrokenSMTP)
        receipt = destination.deliver(b"data", "out.csv")
        assert not receipt.delivered
        assert "connection refused" in (receipt.detail or "")
