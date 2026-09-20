"""The port the server binds is not cosmetic.

A PaaS (Render, Heroku) injects ``PORT`` and routes inbound traffic only to
that port; a service that binds anywhere else fails its deploy with "no open
ports detected". The Dockerfile historically baked ``DATAREADY_PORT=8080``,
which took precedence over the platform's ``PORT`` — so these tests pin the
resolution order that makes a Render deploy bind the right port.
"""

from __future__ import annotations

from app_files.interface.web.main import DEFAULT_PORT, resolve_port


def test_port_is_used_when_it_is_the_only_setting():
    assert resolve_port({"PORT": "10000"}) == 10000


def test_port_wins_over_dataready_port():
    # The regression: DATAREADY_PORT=8080 shipped in the image must not
    # override the port Render scans.
    assert resolve_port({"PORT": "10000", "DATAREADY_PORT": "8080"}) == 10000


def test_dataready_port_applies_without_a_platform_port():
    assert resolve_port({"DATAREADY_PORT": "9000"}) == 9000


def test_default_applies_when_nothing_is_set():
    assert resolve_port({}) == DEFAULT_PORT
    assert DEFAULT_PORT == 8080


def test_a_blank_or_unparseable_value_falls_back():
    assert resolve_port({"PORT": ""}) == DEFAULT_PORT
    assert resolve_port({"PORT": "not-a-number"}) == DEFAULT_PORT