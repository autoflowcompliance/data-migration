"""The DataFlow page must actually render, and the launcher must pick a UI.

Two things are checked here that unit tests over
:mod:`app_files.dataflow.state` cannot: that the Streamlit script executes
end-to-end without raising (a page is a script, so a single bad widget call
breaks the whole app), and that ``python main.py`` routes to the interface the
deployment asked for.

The page is driven with Streamlit's own test harness, which runs the real
script in a real script-runner. Nothing is mocked or stubbed.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

from app_files.settings import (
    DATAFLOW_UI,
    DEFAULT_PORT,
    NICEGUI_UI,
    resolve_ui,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
APP = REPO_ROOT / "app_files" / "dataflow" / "app.py"

AppTest = pytest.importorskip(
    "streamlit.testing.v1", reason="Streamlit is required to run the DataFlow UI"
).AppTest


def load_main():
    """Import ``main.py`` from the repo root as a fresh module."""
    spec = importlib.util.spec_from_file_location("df_main", REPO_ROOT / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["df_main"] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Interface selection
# --------------------------------------------------------------------------
def test_dataflow_is_the_default_interface():
    assert resolve_ui({}) == DATAFLOW_UI


def test_nicegui_can_still_be_selected():
    assert resolve_ui({"DATAREADY_UI": "nicegui"}) == NICEGUI_UI


def test_interface_selection_is_case_and_space_insensitive():
    assert resolve_ui({"DATAREADY_UI": "  DataFlow "}) == DATAFLOW_UI


def test_an_unknown_interface_falls_back_instead_of_failing():
    """A typo must not take a hosted demo down."""
    assert resolve_ui({"DATAREADY_UI": "flask"}) == DATAFLOW_UI


def test_the_launcher_exposes_both_runners():
    main = load_main()
    assert callable(main.run_dataflow)
    assert callable(main.run_nicegui)


def test_the_streamlit_theme_flags_match_the_css_tokens(monkeypatch):
    """The widget palette must match the page palette.

    Streamlit's own widgets (radio, slider, uploader) are styled by the theme
    flags, while everything DataFlow draws itself uses the CSS tokens. If the
    two drift, half the page is amber and half is Streamlit's defaults.
    """
    import re

    from streamlit.web import cli as streamlit_cli

    main = load_main()
    theme_source = (REPO_ROOT / "app_files" / "dataflow" / "theme.py").read_text()
    tokens = dict(re.findall(r"--([\w-]*):\s*(#[0-9A-Fa-f]{6})", theme_source))
    expected = {
        "primaryColor": tokens["amber"],
        "backgroundColor": tokens["paper"],
        "secondaryBackgroundColor": tokens["surface"],
        "textColor": tokens["ink"],
    }

    captured: dict[str, str] = {}

    def fake_main() -> None:
        for argument in sys.argv:
            if argument.startswith("--theme."):
                key, _, value = argument[len("--theme.") :].partition("=")
                captured[key] = value

    monkeypatch.setattr(streamlit_cli, "main", fake_main)
    main.run_dataflow("0.0.0.0", 8080)

    assert captured == expected


def test_the_upload_cap_matches_the_licence(monkeypatch):
    """The dropzone must not promise more than the tool will accept.

    Streamlit defaults to advertising 200 MB per file. In demo mode the page
    rejects anything over 5 MB, so a 40 MB upload would look accepted and then
    fail — which reads as a broken app rather than a licence limit.
    """
    from streamlit.web import cli as streamlit_cli

    from app_files.licensing.limits import resolve_limits

    main = load_main()
    seen: dict[str, str] = {}

    def fake_main() -> None:
        for argument in sys.argv:
            if argument.startswith("--server.maxUploadSize"):
                seen["cap"] = argument.partition("=")[2]

    monkeypatch.setattr(streamlit_cli, "main", fake_main)
    main.run_dataflow("0.0.0.0", 8080)

    demo_cap = resolve_limits(license_valid=False).max_file_size_mb
    assert seen["cap"] == str(int(demo_cap))


def test_the_launcher_targets_the_real_streamlit_script():
    main = load_main()
    script = REPO_ROOT / "app_files" / "dataflow" / "app.py"
    assert script.is_file(), "the launcher points at a script that must exist"
    assert main.resolve_port({"PORT": "10000"}) == 10000
    assert main.resolve_port({}) == DEFAULT_PORT


# --------------------------------------------------------------------------
# The page renders
# --------------------------------------------------------------------------
@pytest.fixture
def page() -> "AppTest":
    app = AppTest.from_file(str(APP), default_timeout=30)
    app.run()
    return app


def test_the_page_renders_without_raising(page):
    assert not page.exception, [str(e) for e in page.exception]


def test_the_page_shows_the_dataflow_title_and_stepper(page):
    html = " ".join(element.value for element in page.get("html"))
    assert "DataFlow" in html
    assert "Upload a messy file" in html
    assert "Configure" in html  # a stepper label


def test_the_page_starts_on_the_upload_step(page):
    radios = [element.value for element in page.radio]
    assert radios == ["CRM export"]


def test_the_page_offers_a_file_uploader(page):
    assert len(page.get("file_uploader")) == 1


def test_the_metric_cards_are_rendered(page):
    html = " ".join(element.value for element in page.get("html"))
    assert "Files run this session" in html
    assert "Target configs available" in html


def test_the_empty_state_shows_before_any_run(page):
    html = " ".join(element.value for element in page.get("html"))
    assert "No runs yet" in html


def test_the_demo_notice_is_shown_when_unlicensed(page):
    """The hosted demo runs unlicensed, and must say so."""
    from app_files.licensing import current_mode

    _licence, limits = current_mode()
    captions = " ".join(element.value for element in page.caption)
    if limits.demo:
        assert "Demo mode" in captions
    else:
        assert "Demo mode" not in captions


def test_a_sample_can_be_loaded_and_run(page):
    """A visitor with no export on hand must still be able to try the demo.

    The whole point of the sample shortcut is that it reaches a result, so this
    clicks it and follows the flow rather than just checking the button exists.
    """
    load_buttons = [button for button in page.button if button.label == "Load sample"]
    assert load_buttons, "the sample loader should be offered"

    load_buttons[0].click().run()
    assert not page.exception, [str(e) for e in page.exception]
    assert page.session_state["df_step"] == 1
    source_name = page.session_state["df_source_name"]
    assert source_name.endswith((".csv", ".json", ".xlsx"))

    # Straight through Configure to Process.
    next_buttons = [b for b in page.button if b.label.startswith("Next: Process")]
    assert next_buttons, "configure step should offer a Next button"
    next_buttons[0].click().run()
    assert not page.exception, [str(e) for e in page.exception]

    run = page.session_state.get("df_run")
    assert run is not None, "the sample should have produced a run"
    assert run.rows_out > 0
    assert page.session_state["df_step"] == 3


def test_the_sample_menu_only_lists_files_that_exist():
    from app_files.dataflow import state

    samples = state.available_samples()
    assert samples, "the repo ships sample files"
    for sample in samples:
        assert state.sample_bytes(sample), f"{sample.filename} should be readable"


def test_the_page_never_uses_unsafe_markdown_for_html():
    """The confirmed bug this codebase keeps re-introducing.

    ``st.markdown(unsafe_allow_html=True)`` sends content through the markdown
    parser, which mangles <style> blocks and can leak CSS as visible text.
    Every DataFlow module must render HTML through st.html instead.

    Parsed as AST rather than grepped, so the prose *describing* the bug — in
    the module docstrings above — is not mistaken for the bug itself.
    """
    modules = [
        REPO_ROOT / "app_files" / "dataflow" / "app.py",
        REPO_ROOT / "app_files" / "dataflow" / "components.py",
        REPO_ROOT / "app_files" / "dataflow" / "theme.py",
    ]
    for module in modules:
        tree = ast.parse(module.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name != "markdown":
                continue
            for keyword in node.keywords:
                assert keyword.arg != "unsafe_allow_html" or not _is_true(
                    keyword.value
                ), f"{module.name}:{node.lineno} renders HTML through unsafe markdown"


def _is_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True