"""Visual rule builder — build validation rules without writing YAML.

This is the implementation, shared by two thin Streamlit pages:

* ``app_files/interface/web/pages/rules.py`` — the new web UI (LAYER 7).
* ``app_files/pages/rule_builder_page.py`` — the original CRM app (its
  ``pages/`` directory is auto-discovered by ``streamlit run app_files/app.py``).

Both call :func:`render`. Keeping one implementation means a change to the
builder cannot land in one app and miss the other.

A buyer who has never written YAML picks a column from the file they just
uploaded, picks one of the five rule types the engine supports, fills in the
fields the form shows them, and presses Add. The rules they build are real YAML
in the same shape as ``app_files/configs/*.yaml`` and
``app_files/rule_library/*.yaml``, and they run through the same rule engine.

There is no model, no API key and no network call: the same form input always
produces the same YAML. The YAML is shown in a collapsible block for buyers who
want to learn the format, and hidden otherwise.

This module imports the builder and the frozen core for use only. Nothing here
modifies either one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Pages set ``__package__`` to "" under `streamlit run`, so the repo root must
# be importable for `app_files...` imports to resolve.
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app_files.ingestion import UnsupportedFormatError, read_any
from app_files.interface.web.display import show
from app_files.mappers import available_crms
from app_files.rules.builder import (
    COMMON_PATTERNS,
    CUSTOM_PATTERN,
    KIND_LABELS,
    DraftError,
    RuleDraft,
    RuleList,
    drafts_from_library,
    parse_rules_yaml,
)
from app_files.rules.execution import run_with_rules
from app_files.utilities.rule_library import load_library

SUPPORTED = ["csv", "tsv", "txt", "json", "xlsx", "xlsm", "xls", "pdf"]

KIND_ORDER = ["required", "format", "length", "range", "list_of_values"]
SEVERITY_LABELS = {"error": "Error", "warning": "Warning", "info": "Info"}
SEVERITY_MARKS = {"error": "✗", "warning": "!", "info": "i"}
LENGTH_MODES = ["Between a minimum and maximum", "Exactly", "At least", "At most"]

_HEADER_HTML = """
    <div style="background:#14181F; border-radius:10px; padding:24px 28px; margin-bottom:16px;">
        <div style="color:#F7F6F3; font-size:1.3rem; font-weight:600;">Rule builder</div>
        <div style="color:#AEB6C2; font-size:.92rem; margin-top:4px;">
            Describe the rules your data must satisfy. No YAML, no regular
            expressions, no code.
        </div>
    </div>
    """


# ------------------------------------------------------------------ session state
def _rule_list() -> RuleList:
    """The session's rule list, created on first use."""
    rules = st.session_state.get("builder_rules")
    if not isinstance(rules, RuleList):
        rules = RuleList()
        st.session_state.builder_rules = rules
    return rules


def _editing_index() -> int | None:
    return st.session_state.get("builder_editing")


def _load_frame(uploaded) -> pd.DataFrame | None:
    if uploaded is None:
        return None
    try:
        return read_any(uploaded.getvalue(), filename=uploaded.name)
    except UnsupportedFormatError as exc:
        st.error(f"Unsupported file type: {exc}")
    except Exception as exc:  # noqa: BLE001 - the UI must never crash
        st.error(f"Could not read that file: {exc}")
    return None


def _int_default(existing: RuleDraft | None, attribute: str, fallback: int) -> int:
    if existing is None:
        return fallback
    value = getattr(existing, attribute, None)
    return int(value) if value is not None else fallback


def _float_default(existing: RuleDraft | None, attribute: str, fallback: float) -> float:
    if existing is None:
        return fallback
    value = getattr(existing, attribute, None)
    return float(value) if value is not None else fallback


def _length_mode(existing: RuleDraft | None) -> int:
    """Which length radio option an existing rule corresponds to."""
    if existing is None:
        return 2
    if existing.exactly is not None:
        return 1
    if existing.min_length is not None and existing.max_length is not None:
        return 0
    if existing.min_length is not None:
        return 2
    if existing.max_length is not None:
        return 3
    return 2


def _clear_form_state() -> None:
    """Drop the form's widget values so pre-filled defaults take effect again.

    Streamlit ignores a widget's ``value=``/``index=`` once its key exists in
    session state, so opening a rule for editing has to clear the keys first or
    the form would keep showing the previously entered values.
    """
    for key in [k for k in st.session_state if str(k).startswith("form_")]:
        del st.session_state[key]


# ------------------------------------------------------------------ the form
def _rule_form(columns: list[str], index: int | None) -> None:
    """The add/edit form. Pre-filled when ``index`` names an existing rule.

    Deliberately not an ``st.form``: widgets inside a form do not rerun until
    submit, so choosing "Valid format" would not reveal the Format dropdown
    until after Add was pressed. Plain widgets rerun on change, which is what
    makes the parameters appear as soon as the rule type is picked.
    """
    rules = _rule_list()
    existing = rules.drafts[index] if index is not None else None

    def _default(attribute: str, fallback):
        return getattr(existing, attribute) if existing is not None else fallback

    st.subheader("Edit rule" if existing is not None else "Build a rule")

    field_name = st.selectbox(
        "Field",
        columns,
        index=columns.index(existing.field) if existing and existing.field in columns else 0,
        key="form_field",
        help="Every column in the file you uploaded.",
    )

    kind = st.selectbox(
        "Rule type",
        KIND_ORDER,
        index=KIND_ORDER.index(existing.kind) if existing else 0,
        format_func=lambda k: KIND_LABELS[k],
        key="form_kind",
    )

    # Parameters default to "not applicable" and are only set for the chosen type.
    format_name = CUSTOM_PATTERN
    pattern = ""
    exactly = min_length = max_length = None
    min_value = max_value = None
    values_text = ""

    if kind == "format":
        format_names = list(COMMON_PATTERNS)
        default_format = _default("format_name", "Email")
        format_name = st.selectbox(
            "Format",
            format_names,
            index=format_names.index(default_format) if default_format in format_names else 0,
            key="form_format",
        )
        if format_name == CUSTOM_PATTERN:
            pattern = st.text_input(
                "Pattern",
                value=_default("pattern", ""),
                key="form_pattern",
                help=r"A regular expression, e.g. ^[A-Z]{2}\d{4}$",
            )
        else:
            st.caption(f"Pattern: `{COMMON_PATTERNS[format_name]}`")

    elif kind == "length":
        mode = st.radio(
            "Length rule", LENGTH_MODES, index=_length_mode(existing), key="form_length_mode"
        )
        if mode == "Exactly":
            exactly = st.number_input(
                "Exactly (characters)",
                min_value=0,
                value=_int_default(existing, "exactly", 10),
                key="form_exactly",
            )
        elif mode == "Between a minimum and maximum":
            min_length = st.number_input(
                "Minimum", min_value=0, value=_int_default(existing, "min_length", 1),
                key="form_min_length",
            )
            max_length = st.number_input(
                "Maximum", min_value=0, value=_int_default(existing, "max_length", 50),
                key="form_max_length",
            )
        elif mode == "At least":
            min_length = st.number_input(
                "Minimum", min_value=0, value=_int_default(existing, "min_length", 1),
                key="form_min_length",
            )
        else:
            max_length = st.number_input(
                "Maximum", min_value=0, value=_int_default(existing, "max_length", 50),
                key="form_max_length",
            )

    elif kind == "range":
        left, right = st.columns(2)
        min_value = left.number_input(
            "Minimum", value=_float_default(existing, "min_value", 0.0), key="form_min_value"
        )
        max_value = right.number_input(
            "Maximum", value=_float_default(existing, "max_value", 100.0), key="form_max_value"
        )

    elif kind == "list_of_values":
        values_text = st.text_area(
            "Allowed values — one per line",
            value="\n".join(existing.values) if existing else "",
            height=120,
            key="form_values",
            help="For example: active, closed, pending",
        )

    severity_options = ["error", "warning", "info"]
    severity = st.selectbox(
        "Severity",
        severity_options,
        index=severity_options.index(_default("severity", "error")),
        format_func=lambda s: SEVERITY_LABELS[s],
        key="form_severity",
    )

    with st.expander("Advanced", expanded=False):
        custom_name = st.text_input(
            "Rule name",
            value=_default("name", ""),
            key="form_name",
            help="Leave blank to name the rule automatically.",
        )
        custom_message = st.text_input(
            "Failure message",
            value=_default("message", ""),
            key="form_message",
            help="Leave blank to use the generated wording.",
        )

    if st.button(
        "Save changes" if existing is not None else "+ Add rule",
        type="primary",
        key="form_submit",
    ):
        draft = RuleDraft(
            field=field_name,
            kind=kind,
            severity=severity,
            name=custom_name,
            message=custom_message,
            format_name=format_name,
            pattern=pattern or "",
            exactly=int(exactly) if exactly is not None else None,
            min_length=int(min_length) if min_length is not None else None,
            max_length=int(max_length) if max_length is not None else None,
            min_value=float(min_value) if min_value is not None else None,
            max_value=float(max_value) if max_value is not None else None,
            values=[line for line in values_text.splitlines() if line.strip()],
        )
        try:
            stored = rules.add(draft) if index is None else rules.replace(index, draft)
        except DraftError as exc:
            st.error(str(exc))
        else:
            st.session_state.builder_editing = None
            st.session_state.builder_notice = (
                f"Added: {stored.describe()}" if index is None else f"Updated: {stored.describe()}"
            )
            _clear_form_state()
            st.rerun()

    if existing is not None and st.button("Cancel edit", key="form_cancel"):
        st.session_state.builder_editing = None
        _clear_form_state()
        st.rerun()


# ------------------------------------------------------------------ the list
def _rule_table() -> None:
    rules = _rule_list()
    st.subheader("Your rules")
    if not len(rules):
        st.info(
            "No rules yet. Build one above, or load a ready-made set from the "
            "**Rule library** tab."
        )
        return

    st.caption(f"{len(rules)} rule(s). They run in the order shown.")
    for index, draft in enumerate(rules.drafts):
        columns = st.columns([0.4, 5.6, 1, 1])
        columns[0].markdown(f"**{SEVERITY_MARKS.get(draft.severity, '•')}**")
        with columns[1]:
            st.markdown(draft.describe())
            st.caption(
                f"`{draft.rule_name()}` · {draft.field} · "
                f"{KIND_LABELS[draft.kind]} · {draft.severity}"
            )
        if columns[2].button("Edit", key=f"edit_{index}"):
            st.session_state.builder_editing = index
            st.rerun()
        if columns[3].button("×", key=f"remove_{index}", help="Remove this rule"):
            removed = rules.remove(index)
            st.session_state.builder_editing = None
            st.session_state.builder_notice = f"Removed: {removed.describe()}"
            st.rerun()

    st.divider()
    left, middle, right = st.columns([2, 1, 1])
    if left.button("Run with these rules", type="primary"):
        st.session_state.builder_run_requested = True
    if middle.button("Clear all"):
        rules.clear()
        st.session_state.builder_editing = None
        st.rerun()
    if right.button("Remove last"):
        if len(rules):
            rules.remove(len(rules) - 1)
        st.rerun()


# ------------------------------------------------------------------ run
def _run_panel(uploaded, frame: pd.DataFrame | None, crm: str) -> None:
    """Run the built rules and show the outcome."""
    rules = _rule_list()
    if not st.session_state.pop("builder_run_requested", False):
        return
    if not len(rules):
        st.warning("Add at least one rule before running.")
        return
    if frame is None:
        st.warning("Upload a file before running.")
        return

    try:
        parsed = rules.to_rules()
    except Exception as exc:  # noqa: BLE001 - a bad rule is a user-facing error
        st.error(f"These rules cannot be run: {exc}")
        return

    with st.spinner("Cleaning, mapping and validating with your rules…"):
        run = run_with_rules(
            frame,
            parsed,
            crm=crm,
            rules_path="workspace/rules.yaml",
            source_filename=uploaded.name if uploaded is not None else "upload.csv",
        )

    summary = run.summary()
    st.subheader("Result")
    metrics = st.columns(4)
    metrics[0].metric("Rows in", summary.get("rows_in", 0))
    metrics[1].metric("Rows out", summary.get("rows_out", 0))
    metrics[2].metric("Rule failures", summary.get("rule_failures", 0))
    metrics[3].metric("Quality score", f"{summary.get('quality_score', 0)}%")

    if summary.get("rule_failures"):
        st.warning(
            f"{summary['rule_failures']} failure(s) across "
            f"{summary.get('rules_run', 0)} rule(s)."
        )
    else:
        st.success(f"All {summary.get('rules_run', 0)} rule(s) passed.")

    # A rule that matched no column would otherwise look like a pass.
    if run.unmatched_rules:
        st.warning(
            "These rules did not run because their field is not in the cleaned "
            "output: " + ", ".join(run.unmatched_rules) + ". "
            "Pick a field that exists in the file, or choose a different target config."
        )

    st.caption(f"Rules written to `{run.rules_path}`.")
    show(run.rules_frame())

    issues = run.issues_frame()
    with st.expander(f"Every issue ({len(issues)})", expanded=bool(len(issues))):
        if issues.empty:
            st.success("No issues found.")
        else:
            show(issues)

    st.download_button(
        "Download QA report (HTML)",
        run.qa_report_html,
        file_name="qa_report.html",
        mime="text/html",
    )


# ------------------------------------------------------------------ library tab
def _library_tab(columns: list[str]) -> None:
    st.subheader("Rule library")
    st.caption(
        "Ready-made rule sets. Load one to start from something that works, "
        "then adjust it in the builder."
    )
    library = load_library()
    if not library:
        st.info("No rule sets are installed.")
        return

    for name, rule_set in library.items():
        drafts = drafts_from_library(rule_set.rules, columns)
        with st.expander(f"{rule_set.title} — {len(drafts)} rule(s)"):
            st.write(rule_set.summary)
            expects = ", ".join(f"`{column}`" for column in rule_set.expects) or "—"
            st.caption(f"Expects: {expects}")
            # Report against the fields the rules were actually pointed at, not
            # the library's own vocabulary, so a repointed rule is not called missing.
            if columns:
                missing = [d.field for d in drafts if d.field not in columns]
                if missing:
                    st.warning(
                        "These rules would not run on this file because the field "
                        "is not present: " + ", ".join(sorted(set(missing))) + ". "
                        "Edit the field after loading."
                    )
            if st.button("Load", key=f"load_{name}"):
                if not drafts:
                    st.warning("That set has no rules the builder can represent.")
                else:
                    added = _rule_list().extend(drafts)
                    st.session_state.builder_notice = (
                        f"Loaded {len(added)} rule(s) from {rule_set.title}."
                    )
                    st.rerun()


# ------------------------------------------------------------------ YAML view
def _yaml_section() -> None:
    """The read-only YAML view, for buyers who want to learn the format."""
    yaml_text = _rule_list().to_yaml()
    with st.expander("View as YAML", expanded=False):
        st.caption(
            "This is exactly what gets written to `workspace/rules.yaml` and "
            "handed to the rule engine. You never need to edit it by hand."
        )
        st.code(yaml_text, language="yaml")
        try:
            parsed = parse_rules_yaml(yaml_text)
        except Exception as exc:  # noqa: BLE001
            st.error(f"This YAML is not valid: {exc}")
        else:
            st.success(f"Valid — {len(parsed)} rule(s) the engine can run.")
        st.download_button(
            "Download rules.yaml", yaml_text, file_name="rules.yaml", mime="text/yaml"
        )


# ------------------------------------------------------------------ main
def render(*, show_header: bool = True) -> None:
    """Draw the whole rule builder into the current Streamlit page.

    ``show_header`` is False when the host page already renders its own title.
    """
    if show_header:
        st.html(_HEADER_HTML)

    notice = st.session_state.pop("builder_notice", None)
    if notice:
        st.success(notice)

    uploaded = st.file_uploader(
        "Upload the file you want to validate",
        type=SUPPORTED,
        help="The columns of this file populate the Field dropdown.",
    )
    frame = _load_frame(uploaded)
    if frame is not None:
        st.success(
            f"Read **{len(frame):,}** rows and **{len(frame.columns)}** columns "
            f"from `{uploaded.name}`."
        )

    crms = available_crms()
    with st.sidebar:
        st.header("Run settings")
        crm = st.selectbox(
            "Target config",
            crms,
            index=crms.index("hubspot") if "hubspot" in crms else 0,
            help="Your rules run on top of this config's cleaning and mapping.",
        )

    columns = [str(c) for c in frame.columns] if frame is not None else []
    build_tab, library_tab = st.tabs(["Build rules", "Rule library"])

    with build_tab:
        if frame is None:
            st.info("Upload a file to see available fields.")
        else:
            _rule_form(columns, _editing_index())
            st.divider()
            _rule_table()
            st.divider()
            _run_panel(uploaded, frame, crm)
            st.divider()
            _yaml_section()

    with library_tab:
        _library_tab(columns)