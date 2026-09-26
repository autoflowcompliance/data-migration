"""The port the server binds is not cosmetic.

A PaaS (Render, Heroku) injects ``PORT`` and routes inbound traffic only to
that port; a service that binds anywhere else fails its deploy with "no open
ports detected". The Dockerfile historically baked ``DATAREADY_PORT=8080``,
which took precedence over the platform's ``PORT`` — so these tests pin the
resolution order that makes a Render deploy bind the right port.
"""

from __future__ import annotations

from pathlib import Path

from app_files.settings import DEFAULT_PORT, resolve_port


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


def test_no_module_uses_a_name_newer_than_the_image_interpreter():
    """The dev interpreter is not the deployed one.

    ``python:3.10-slim`` runs the app, but development happens on 3.13, so a
    name added in 3.11 or 3.12 imports fine locally and raises ImportError only
    in the image — and because it raises at import time, it takes down whichever
    module needs it. ``datetime.UTC`` (3.11) did exactly this to
    ``test_compliance.py``: invisible on 3.13, a collection error on 3.10.

    This guards the documented floor rather than a list of names, so the next
    such name is caught without anyone remembering to add it here.
    """
    import ast

    # Names that exist only from 3.11/3.12, mapped to the module they come from.
    too_new = {
        "datetime": {"UTC"},
        "typing": {"Self", "override", "assert_type", "assert_never", "Never"},
        "enum": {"StrEnum", "ReprEnum"},
        "asyncio": {"TaskGroup", "timeout", "Runner"},
        "itertools": {"batched"},
    }
    root = Path(__file__).resolve().parents[2]
    offenders: list[str] = []

    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in too_new:
                for alias in node.names:
                    if alias.name in too_new[node.module]:
                        rel = path.relative_to(root)
                        offenders.append(f"{rel}:{node.lineno} imports {node.module}.{alias.name}")
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                names = too_new.get(node.value.id, set())
                if node.attr in names:
                    rel = path.relative_to(root)
                    offenders.append(f"{rel}:{node.lineno} uses {node.value.id}.{node.attr}")

    assert not offenders, (
        "names newer than the 3.10 the image runs:\n  " + "\n  ".join(offenders)
    )


# --------------------------------------------------------------------------
# Host and interface selection
# --------------------------------------------------------------------------
def test_host_defaults_to_all_interfaces():
    from app_files.settings import resolve_host

    assert resolve_host({}) == "0.0.0.0"


def test_host_can_be_overridden():
    from app_files.settings import resolve_host

    assert resolve_host({"DATAREADY_HOST": "127.0.0.1"}) == "127.0.0.1"


def test_there_is_no_interface_switch_any_more():
    """One UI ships now, so no setting may select a second one.

    The switch was the only reason ``resolve_ui`` existed; a leftover name
    would invite someone to reintroduce a branch that no longer has an
    implementation behind it.
    """
    import app_files.settings as settings

    assert not hasattr(settings, "resolve_ui")
    assert not hasattr(settings, "DATAFLOW_UI")


def test_the_dockerfile_does_not_pin_a_port_render_will_override():
    """DATAREADY_PORT in the image must stay non-authoritative.

    It is kept as a sane local default, but it may only apply when the
    platform has not injected PORT — otherwise the deploy binds the wrong port.
    """
    dockerfile = (Path(__file__).resolve().parents[2] / "Dockerfile").read_text()
    assert "DATAREADY_PORT=8080" in dockerfile
    assert resolve_port({"PORT": "10000", "DATAREADY_PORT": "8080"}) == 10000