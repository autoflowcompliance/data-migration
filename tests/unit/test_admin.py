"""The admin console snapshot and page."""

from __future__ import annotations

from pathlib import Path

from app_files.admin import render_admin_html, snapshot, write_admin_snapshot


def test_the_snapshot_has_every_section():
    state = snapshot()
    body = state.as_dict()
    assert set(body) == {"runs", "trend", "tenants", "formats", "connectors", "health"}


def test_formats_include_the_builtins():
    body = snapshot().as_dict()
    assert {"csv", "excel", "json", "sql"} <= set(body["formats"]["builtin"])


def test_the_health_section_is_populated():
    body = snapshot().as_dict()
    assert "checks" in body["health"]
    assert "ok" in body["health"]


def test_connectors_are_listed():
    providers = {c["provider"] for c in snapshot().as_dict()["connectors"]}
    assert "s3" in providers


def test_the_page_renders_the_sections():
    html = render_admin_html(snapshot())
    assert html.startswith("<!doctype html>")
    for heading in ("Recent runs", "Tenants", "Connectors", "Output formats"):
        assert heading in html


def test_an_empty_install_still_renders():
    html = render_admin_html(snapshot())
    assert "Nothing yet." in html or "csv" in html


def test_the_page_can_be_written(tmp_path):
    written = write_admin_snapshot(snapshot(), str(tmp_path / "admin.html"))
    assert Path(written).exists()
    assert "Admin console" in Path(written).read_text()