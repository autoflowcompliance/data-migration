"""The upload handlers must speak this NiceGUI's upload API.

NiceGUI 3.x replaced the 1.x ``event.content`` / ``event.name`` pair with a
single ``event.file`` object whose ``read()`` is async and whose name lives on
``.name``. The handlers here were written against the 1.x shape, so every real
upload raised ``AttributeError`` inside NiceGUI's exception handler — which
swallows it and leaves the page looking untouched. The sample button still
worked, so the demo looked healthy while the actual product did not.

These tests drive the real ``UploadFile`` object NiceGUI constructs, so a
future API change fails here instead of in a visitor's browser.
"""

from __future__ import annotations

import ast
import io
from pathlib import Path

import pytest
from nicegui import events
from nicegui.elements.upload_files import SmallFileUpload

from app_files.interface.web.routes import branding as branding_route
from app_files.interface.web.routes import upload as upload_route

SAMPLE = Path(__file__).resolve().parents[2] / "app_files" / "samples" / "messy_contacts.csv"


def _two_column_csv() -> bytes:
    """A bank/ledger-shaped CSV, for the two reconciliation uploaders."""
    return b"Date,Amount\n2024-01-01,10.00\n2024-01-02,-5.00\n"


def _upload_event(data: bytes, name: str) -> events.UploadEventArguments:
    """The event NiceGUI really hands an ``on_upload`` handler."""
    return events.UploadEventArguments(
        sender=None, client=None,
        file=SmallFileUpload(name, "text/csv", data),
    )


def _handlers() -> dict[str, object]:
    """The upload callbacks, pulled out of the page body.

    They are closures over the page's widgets, so they cannot be imported; the
    source is the only handle on them. Executing it against a stub ``ui`` and
    stub collaborators gives real callables to call with a real event.
    """
    source = Path(upload_route.__file__).read_text()
    tree = ast.parse(source)
    wanted = {"handle_crm_upload", "handle_bank_upload", "handle_ledger_upload"}
    found = {}

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name in wanted:
                found[child.name] = child
            visit(child)

    visit(tree)
    assert set(found) == wanted, f"missing handlers: {wanted - set(found)}"
    return found


@pytest.mark.parametrize("handler", ["handle_crm_upload", "handle_bank_upload", "handle_ledger_upload"])
def test_every_upload_handler_reads_the_file_through_the_real_api(handler):
    """Each handler is async and reaches the bytes via ``event.file``."""
    node = _handlers()[handler]
    assert isinstance(node, ast.AsyncFunctionDef), (
        f"{handler} must be async: NiceGUI 3.x file reads are awaitable"
    )

    source = ast.get_source_segment(Path(upload_route.__file__).read_text(), node)
    assert "event.file" in source, f"{handler} does not read event.file"
    assert "event.content" not in source, f"{handler} still uses the NiceGUI 1.x event.content"
    assert "event.name" not in source, f"{handler} still uses the NiceGUI 1.x event.name"


def test_the_logo_handler_reads_the_file_through_the_real_api():
    source = Path(branding_route.__file__).read_text()
    assert "event.file" in source
    assert "event.content" not in source, "branding still uses the NiceGUI 1.x event.content"
    assert "event.name" not in source, "branding still uses the NiceGUI 1.x event.name"


@pytest.mark.asyncio
async def test_the_event_object_has_no_content_or_name_and_the_new_api_works():
    """Pins the API shape itself, so the tests above cannot go stale silently."""
    event = _upload_event(SAMPLE.read_bytes(), "messy_contacts.csv")

    assert not hasattr(event, "content"), "this NiceGUI reintroduced event.content"
    assert not hasattr(event, "name"), "this NiceGUI reintroduced event.name"

    data = await event.file.read()
    assert event.file.name == "messy_contacts.csv"
    assert data == SAMPLE.read_bytes()
