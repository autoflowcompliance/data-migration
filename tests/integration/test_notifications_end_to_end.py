"""A run tells the outside world, end to end.

Drives the real CLI with ``--notify`` against a real HTTP listener on a
loopback port, over a real config file, so "an external system is notified"
means an actual POST arrived and not that a mock saw a call. Also drives the
library entry point, so the binding is covered where a scheduled runner would
reach it.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from app_files.cli import main
from app_files.observability import notify_run

GOLDEN = Path(__file__).resolve().parent.parent / "regression" / "golden_files" / "quality_history"


class _Collector(BaseHTTPRequestHandler):
    """Records every POST body on the server instance."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.server.received.append(
            {"body": json.loads(body), "headers": dict(self.headers), "path": self.path}
        )
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):  # keep pytest output clean
        pass


@pytest.fixture
def listener():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Collector)
    server.received = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, f"http://127.0.0.1:{server.server_address[1]}/hook"
    finally:
        server.shutdown()
        server.server_close()


def _config(tmp_path: Path, url: str, *, required: bool = False) -> Path:
    path = tmp_path / "crm.yaml"
    required_line = "    required: true\n" if required else ""
    path.write_text(
        "crm: Contacts\n"
        'version: "1.0"\n'
        "fields:\n"
        "  - name: email\n"
        '    aliases: ["Email Address"]\n'
        f"{required_line}"
        "notifications:\n"
        f"  webhooks:\n    - url: {url}\n",
        encoding="utf-8",
    )
    return path


class TestCliNotify:
    def test_a_completed_run_posts_to_a_real_listener(self, listener, tmp_path, monkeypatch):
        server, url = listener
        config = _config(tmp_path, url)
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        code = main(
            [
                "-i", str(GOLDEN / "contacts.csv"),
                "-c", str(config),
                "-o", str(tmp_path / "out"),
                "--notify",
            ]
        )
        assert code == 0
        assert len(server.received) == 1
        payload = server.received[0]["body"]
        assert payload["event"] == "run.completed"
        assert payload["status"] == "completed"
        assert payload["quality_score"] == 100.0
        assert payload["output_location"] == str(tmp_path / "out")

    def test_a_failed_run_posts_failed(self, listener, tmp_path, monkeypatch):
        server, url = listener
        config = _config(tmp_path, url, required=True)
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        # The config requires email; a file with no such column fails validation.
        broken = tmp_path / "broken.csv"
        broken.write_text("name\nAnn\n", encoding="utf-8")
        code = main(
            [
                "-i", str(broken),
                "-c", str(config),
                "-o", str(tmp_path / "out"),
                "--notify",
            ]
        )
        assert code != 0
        assert len(server.received) == 1
        assert server.received[0]["body"]["event"] == "run.failed"

    def test_without_the_flag_no_post_is_made(self, listener, tmp_path, monkeypatch):
        server, url = listener
        config = _config(tmp_path, url)
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        main(
            [
                "-i", str(GOLDEN / "contacts.csv"),
                "-c", str(config),
                "-o", str(tmp_path / "out"),
            ]
        )
        assert server.received == []


class TestLibraryNotify:
    def test_the_binding_posts_a_real_summary(self, listener, tmp_path):
        server, url = listener
        config = _config(tmp_path, url)

        outcome = notify_run(
            config,
            {"status": "ok", "quality_score": 88.0, "rows_in": 5, "rows_out": 5},
            run_id="run-42",
            output_location="/tmp/out",
            source="contacts",
        )
        assert outcome is not None
        assert outcome.delivered is True
        assert len(server.received) == 1
        payload = server.received[0]["body"]
        assert payload["run_id"] == "run-42"
        assert payload["source"] == "contacts"
        assert payload["rows_in"] == 5


class TestBatchNotify:
    def test_each_file_in_a_batch_posts(self, listener, tmp_path, monkeypatch):
        import shutil

        server, url = listener
        config = tmp_path / "batch.yaml"
        config.write_text(
            "crm: Contacts\n"
            "fields:\n"
            '  - name: email\n'
            '    aliases: ["Email Address"]\n'
            "notifications:\n"
            f"  webhooks:\n    - url: {url}\n",
            encoding="utf-8",
        )
        inbox = tmp_path / "inbox"
        inbox.mkdir()
        for name in ("a.csv", "b.csv"):
            shutil.copy(GOLDEN / "contacts.csv", inbox / name)
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        code = main(
            [
                "batch",
                "--in", str(inbox),
                "--template", str(config),
                "--out", str(tmp_path / "out"),
                "--notify",
            ]
        )
        assert code == 0
        assert len(server.received) == 2
        assert {r["body"]["source"] for r in server.received} == {"a", "b"}
