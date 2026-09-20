"""Utility suite — one page for the twelve capabilities.

Lives in ``app_files/pages/``, so Streamlit's native multipage navigation
discovers it automatically. Kept separate from the CRM tool and the reconciliation
page: this file imports the utilities layer and the frozen core, and nothing here
can break either of them.

Twelve tools, one tab each:

1  data quality score      — a single number, plus what dragged it down
2  what was fixed          — a plain-English paragraph about the last run
3  before/after diff       — side-by-side, changes highlighted
4  lineage explorer        — every transformation, searchable
5  reconciliation          — matched / missing / never cleared / variance
6  template marketplace    — browse and install template packs
7  sample data generator   — messy data for any schema, no real file needed
8  export                  — csv, excel, json, sql, pdf, html
9  client workspaces       — one folder per client
10 audit trail             — hashed record of every run
11 rule library            — pick rule sets instead of writing YAML
12 install verifier        — confirm the tool works on this machine
13 share & contracts        — self-contained HTML report, enforced data contract
14 intelligence            — suggestions, plain-English queries/rules, drift
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app_files.collaboration.comparison import build_comparison, render_comparison_html
from app_files.collaboration.contracts import (
    ContractError,
    available_contracts,
    check_contract,
    render_contract_html,
)
from app_files.collaboration.shareable_report import build_from_result
from app_files.collaboration.workspaces import (
    WorkspaceError,
    get_workspace,
    list_workspaces,
    run_in_workspace,
)
from app_files.ingestion import UnsupportedFormatError, read_any
from app_files.interface.web.display import show
from app_files.intelligence import nl_query
from app_files.intelligence.anomaly import clear_baselines, detect, render_anomaly_html
from app_files.intelligence.suggestions import render_suggestions_html, suggest
from app_files.lineage import LineageTracker
from app_files.lineage.report import render_lineage_html
from app_files.mappers import available_crms
from app_files.onboarding.verifier import run_checks
from app_files.pipeline import run_pipeline
from app_files.profiling import profile, scorecard_rows
from app_files.services.bank_reconciliation.reconciler import (
    UnreadableStatementError,
    run_reconciliation,
)
from app_files.utilities.exports import available_formats, write_any_extended
from app_files.utilities.fix_summary import write_summary
from app_files.utilities.marketplace import catalog_frame, marketplace_summary
from app_files.utilities.reconciliation_dashboard import build_dashboard, render_dashboard_html
from app_files.utilities.rule_library import available_rule_sets, rule_library_frame, validate_rule_set
from app_files.utilities.sample_generator import available_profiles, generate, schema_description

st.set_page_config(page_title="Utility suite", page_icon="◆", layout="wide")

st.html(
    """
    <div style="background:#14181F; border-radius:10px; padding:24px 28px; margin-bottom:16px;">
        <div style="color:#F7F6F3; font-size:1.3rem; font-weight:600;">Utility suite</div>
        <div style="color:#AEB6C2; font-size:.92rem; margin-top:4px;">
            Score your data, see exactly what changed, trace every edit, and export
            to whatever your target system needs.
        </div>
    </div>
    """
)


# --------------------------------------------------------------------- helpers
def _load_uploaded(uploaded) -> pd.DataFrame | None:
    """Read an uploaded file through the real ingestion layer."""
    if uploaded is None:
        return None
    try:
        return read_any(uploaded.getvalue(), filename=uploaded.name)
    except UnsupportedFormatError as exc:
        st.error(f"Unsupported file type: {exc}")
    except Exception as exc:  # noqa: BLE001 - the UI must never crash
        st.error(f"Could not read that file: {exc}")
    return None


def _current_frame() -> pd.DataFrame | None:
    """The frame the other tabs work on: uploaded now, or from the last run."""
    uploaded = st.session_state.get("utility_upload")
    if uploaded is not None:
        return _load_uploaded(uploaded)
    return st.session_state.get("utility_frame")


@st.cache_data(show_spinner=False)
def _run_cached(data: bytes, filename: str, crm: str) -> dict:
    """Run the pipeline once per (file, target) and reuse the result across tabs."""
    tracker = LineageTracker()
    frame = read_any(data, filename=filename)
    result = run_pipeline(
        frame, crm=crm, lineage_tracker=tracker, source_filename=filename
    )
    return {
        "result": result,
        "tracker": tracker,
        "original": frame,
        "clean": result.clean_frame,
        "profile": profile(result.clean_frame),
    }


_tabs = st.tabs(
    [
        "Quality score",
        "What was fixed",
        "Before / after",
        "Lineage",
        "Reconciliation",
        "Marketplace",
        "Sample data",
        "Export",
        "Workspaces",
        "Audit trail",
        "Rule library",
        "Install check",
        "Share & contracts",
        "Intelligence",
    ]
)


def _source_controls(label: str = "Your file", prefix: str = "shared"):
    """Upload + target selector, shared by the tabs that need a run.

    Every tab renders its own copy, so the widget keys must be unique per tab —
    Streamlit raises on a duplicate key within one page render.
    """
    column_a, column_b = st.columns([2, 1])
    with column_a:
        uploaded = st.file_uploader(
            label, type=["csv", "tsv", "txt", "json", "xlsx", "xlsm", "xls", "pdf"],
            key=f"{prefix}_upload",
        )
    with column_b:
        crm = st.selectbox("Target system", available_crms(), key=f"{prefix}_crm")
    return uploaded, crm


def _ensure_result(uploaded, crm: str) -> dict | None:
    if uploaded is None:
        return None
    try:
        return _run_cached(uploaded.getvalue(), uploaded.name, crm)
    except Exception as exc:  # noqa: BLE001 - report, never raise into the UI
        st.error(f"Could not process that file: {exc}")
        return None


# ------------------------------------------------------- 1. quality score
with _tabs[0]:
    _uploaded, _crm = _source_controls(prefix="score")
    st.subheader("One-click data quality score")
    st.caption("A single number out of 100, the five dimensions behind it, and the columns that dragged it down.")
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        prof = bundle["profile"]
        left, middle = st.columns([1, 2])
        with left:
            st.metric("Overall score", f"{prof.overall:.0f} / 100")
        with middle:
            show(pd.DataFrame(scorecard_rows(prof)), use_container_width=True)
        # Two different scores exist for the same file and they are not
        # interchangeable. The profile score averages five dimensions across all
        # cells; the validation score counts rows carrying at least one rule
        # failure. A file whose cells are mostly complete can still lose many
        # whole rows to a single required field, so the two drift apart. Both
        # are labelled here rather than picking one and hiding the other.
        validation_score = bundle["result"].summary().get("quality_score")
        st.info(
            f"**Two scores, two questions.** This tab answers *how good are the "
            f"values?* — the profile score **{prof.overall:.0f} / 100** averages "
            f"completeness, uniqueness, validity, consistency and timeliness "
            f"across every cell. The pipeline's validation score is "
            f"**{validation_score} / 100**, which counts rows with at least one "
            f"rule failure. See the **What was fixed** tab for that one."
        )
        worst = sorted(prof.column_scores.items(), key=lambda item: item[1])[:5]
        st.markdown("**Columns pulling the score down**")
        if worst:
            show(
                pd.DataFrame(worst, columns=["column", "score"]),
                use_container_width=True,
            )
        else:
            st.info("No weak columns found.")
    else:
        st.info("Upload a file to score it.")

# ----------------------------------------------------- 2. what was fixed
with _tabs[1]:
    _uploaded, _crm = _source_controls(prefix="fixed")
    st.subheader("What was fixed")
    st.caption("One plain-English paragraph describing the last run.")
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        fix = write_summary(bundle["result"], original=bundle["original"])
        st.success(fix.paragraph())
        # The counterpart to the note on the Quality score tab: this score is
        # row-based, not cell-based, and will differ from the profile score.
        st.caption(
            f"Validation score **{fix.quality_score} / 100** counts rows with at "
            "least one rule failure — see the Quality score tab for the "
            "separate cell-level profile score."
        )
        with st.expander("The numbers behind that sentence"):
            from app_files.utilities.fix_summary import summary_frame

            show(summary_frame(fix), use_container_width=True)
    else:
        st.info("Upload a file to see what would be fixed.")

# ------------------------------------------------------ 3. before / after
with _tabs[2]:
    _uploaded, _crm = _source_controls(prefix="beforeafter")
    st.subheader("Before and after")
    st.caption("Side by side. Changed cells are highlighted; removed rows are marked red.")
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        comparison = build_comparison(
            bundle["original"], bundle["tracker"], bundle["clean"]
        )
        show(pd.DataFrame([comparison.summary()]), use_container_width=True)
        st.html(render_comparison_html(comparison))
    else:
        st.info("Upload a file to compare it with its cleaned version.")

# ---------------------------------------------------------- 4. lineage
with _tabs[3]:
    _uploaded, _crm = _source_controls(prefix="lineage")
    st.subheader("Lineage explorer")
    st.caption("Every transformation that touched your data, searchable.")
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        tracker = bundle["tracker"]
        frame = tracker.to_frame()
        st.metric("Transformations recorded", f"{len(frame):,}")
        if not frame.empty:
            search = st.text_input("Filter (column, action or value)")
            shown = frame
            if search:
                mask = frame.astype(str).apply(
                    lambda column: column.str.contains(search, case=False, na=False)
                ).any(axis=1)
                shown = frame[mask]
                st.caption(f"{len(shown)} of {len(frame)} rows match.")
            show(shown, use_container_width=True, height=320)
            st.html(render_lineage_html(tracker, limit=100))
    else:
        st.info("Upload a file to record its lineage.")

# ---------------------------------------------------- 5. reconciliation
with _tabs[4]:
    st.subheader("Reconciliation dashboard")
    st.caption("Matched, missing from the books, never cleared, date drift and total variance — one screen.")
    statement = st.file_uploader("Bank statement", type=["csv", "pdf"], key="recon_statement")
    ledger = st.file_uploader("Your ledger", type=["csv", "xlsx"], key="recon_ledger")
    tolerance = st.slider("Date tolerance (days)", 0, 10, 2)
    if statement and ledger:
        try:
            statement_frame = read_any(statement.getvalue(), filename=statement.name)
            ledger_frame = read_any(ledger.getvalue(), filename=ledger.name)
            if "Date" not in ledger_frame.columns or "Amount" not in ledger_frame.columns:
                st.error("The ledger needs Date, Description and Amount columns.")
            else:
                result = run_reconciliation(
                    statement.getvalue(),
                    ledger.getvalue(),
                    "Date",
                    "Amount",
                    "Date",
                    "Amount",
                    date_tolerance_days=tolerance,
                )
                dashboard = build_dashboard(result, amount_column="Amount", tolerance_days=tolerance)
                summary = dashboard.summary
                columns = st.columns(5)
                columns[0].metric("Matched", summary.matched)
                columns[1].metric("Missing from books", summary.missing_from_books)
                columns[2].metric("Never cleared", summary.never_cleared)
                columns[3].metric("Date drift", summary.date_drift)
                columns[4].metric("Variance", f"{summary.total_variance:,.2f}")
                st.html(render_dashboard_html(dashboard, title="Reconciliation"))
        except UnreadableStatementError as exc:
            st.error(f"Could not read the statement: {exc}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not reconcile those files: {exc}")
    else:
        st.info("Upload a statement and a ledger to reconcile them.")

# ------------------------------------------------------ 6. marketplace
with _tabs[5]:
    st.subheader("Template marketplace")
    summary = marketplace_summary()
    columns = st.columns(4)
    columns[0].metric("Installed", summary["installed"])
    columns[1].metric("Free", summary["free"])
    columns[2].metric("Paid", summary["paid"])
    columns[3].metric("Incomplete", len(summary["incomplete"]))
    st.caption(f"Installed packs live in {summary['directory']}")
    show(catalog_frame(), use_container_width=True)

# ----------------------------------------------------- 7. sample data
with _tabs[6]:
    st.subheader("Sample data generator")
    st.caption("Deliberately messy test data for any schema. Try the tool before uploading anything real.")
    chosen = st.selectbox("Profile", available_profiles())
    columns_a, columns_b, columns_c = st.columns(3)
    rows = columns_a.number_input("Rows", 5, 5000, 50, step=5)
    seed = columns_b.number_input("Seed", 0, 9999, 42, help="Same seed, same file.")
    duplicate_rate = columns_c.slider("Duplicate rate", 0.0, 0.5, 0.1)
    if chosen:
        described = schema_description(chosen)
        st.markdown(f"**{described['description']}**")
        show(pd.DataFrame(described["columns"]), use_container_width=True)
        generated = generate(chosen, rows=int(rows), seed=int(seed), duplicate_rate=duplicate_rate)
        show(generated.head(20), use_container_width=True)
        st.download_button(
            "Download this sample",
            generated.to_csv(index=False).encode("utf-8"),
            file_name=f"{chosen}_sample.csv",
            mime="text/csv",
        )

# ---------------------------------------------------------- 8. export
with _tabs[7]:
    _uploaded, _crm = _source_controls(prefix="export")
    st.subheader("Export to any format")
    st.caption("CSV, Excel, JSON, SQL, PDF report and HTML dashboard — whatever the target system needs.")
    bundle = _ensure_result(_uploaded, _crm)
    output_format = st.selectbox("Format", available_formats())
    if bundle:
        clean = bundle["clean"]
        fix = write_summary(bundle["result"], original=bundle["original"])
        import tempfile

        target = Path(tempfile.mkdtemp()) / "export_out"
        path = write_any_extended(
            clean,
            target,
            output_format,
            summary=fix,
            source_filename=_uploaded.name,
            project_name="Utility suite",
        )
        st.success(f"Wrote {path.name} ({path.stat().st_size:,} bytes).")
        st.download_button(
            f"Download {path.name}",
            path.read_bytes(),
            file_name=path.name,
            mime="application/octet-stream",
        )
    else:
        st.info("Upload a file to export it.")

# ------------------------------------------------------ 9. workspaces
with _tabs[8]:
    st.subheader("Client workspaces")
    st.caption("One folder per client: configs, samples and outputs never mix.")
    existing = list_workspaces()
    if existing:
        st.markdown("**Existing workspaces:** " + ", ".join(existing))
    else:
        st.info("No workspaces yet.")
    with st.form("workspace_run"):
        client = st.text_input("Client name", placeholder="e.g. Acme Corp")
        workspace_file = st.file_uploader(
            "File to process", type=["csv", "tsv", "txt", "json", "xlsx", "xlsm", "xls", "pdf"],
            key="workspace_file",
        )
        workspace_crm = st.selectbox("Target system", available_crms(), key="workspace_crm")
        submitted = st.form_submit_button("Process in workspace")
    if submitted:
        if not client or workspace_file is None:
            st.error("A client name and a file are both required.")
        else:
            import tempfile

            holding = Path(tempfile.mkdtemp()) / workspace_file.name
            holding.write_bytes(workspace_file.getvalue())
            try:
                outcome = run_in_workspace(client, holding, config=workspace_crm)
                st.success(f"Processed {outcome.summary()['input']} for {client}.")
                st.json(outcome.summary())
                workspace = get_workspace(client, create=False)
                st.code("\n".join(workspace.tree()), language="text")
            except WorkspaceError as exc:
                st.error(str(exc))
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not process that file: {exc}")

# ----------------------------------------------------- 10. audit trail
with _tabs[9]:
    st.subheader("Audit trail")
    st.caption("Every run, with a hash of its output. If a client asks what you did to their data, this is the answer.")
    from app_files.collaboration.audit_trail import read_log

    entries = read_log()
    if entries:
        table = pd.DataFrame(entries)
        show(table, use_container_width=True)
        st.download_button(
            "Download audit log (JSON)",
            pd.DataFrame(entries).to_json(orient="records", indent=2).encode("utf-8"),
            file_name="audit_trail.json",
            mime="application/json",
        )
    else:
        st.info("No runs recorded yet. Runs from the Workspaces tab are logged automatically.")

# --------------------------------------------------- 11. rule library
with _tabs[10]:
    _uploaded, _crm = _source_controls(prefix="rules")
    st.subheader("Rule library")
    st.caption("Pick the rules you need. No YAML.")
    bundle = _ensure_result(_uploaded, _crm)
    show(rule_library_frame(), use_container_width=True)
    chosen_rules = st.multiselect("Apply rule sets", available_rule_sets())
    if chosen_rules and bundle:
        for name in chosen_rules:
            outcome = validate_rule_set(name, bundle["clean"])
            if not outcome["applicable"]:
                st.warning(
                    f"{outcome['title']}: skipped — your file has no column called "
                    f"{', '.join(outcome['columns_missing'])}."
                )
                continue
            if outcome["failures"]:
                st.error(
                    f"{outcome['title']}: {outcome['failures']} of {outcome['rules_run']} "
                    f"rule checks failed."
                )
                show(
                    pd.DataFrame(
                        [{"rule": k, "failures": v} for k, v in outcome["failures_by_rule"].items()]
                    ),
                    use_container_width=True,
                )
            else:
                st.success(f"{outcome['title']}: passed.")
    elif chosen_rules:
        st.info("Upload a file to apply those rules.")

# --------------------------------------------------- 12. install check
with _tabs[11]:
    st.subheader("Install check")
    st.caption("Confirms the tool works on this machine before you rely on it.")
    if st.button("Run the install check"):
        report = run_checks()
        for check in report.checks:
            (st.success if check.passed else st.error)(f"{check.name}: {check.detail}")
        summary = report.summary()
        if summary["ok"]:
            st.markdown(f"**All clear — {summary['passed']} of {summary['total']} checks passed.**")
        else:
            st.markdown(f"**{summary['failed']} check(s) failed: {', '.join(summary['failed'])}**")

# ------------------------------------------- 13. share & data contracts
with _tabs[12]:
    _uploaded, _crm = _source_controls(prefix="share")
    st.subheader("Share and enforce")
    st.caption(
        "One self-contained HTML report you can email or drop in Slack, and a "
        "contract that defines what good data means for this pipeline."
    )
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        import tempfile

        fix = write_summary(bundle["result"], original=bundle["original"])
        share_html = build_from_result(
            bundle["result"],
            summary_paragraph=fix.paragraph(),
            source_filename=_uploaded.name,
            project_name="Utility suite",
            crm=_crm,
        )
        target = Path(tempfile.mkdtemp()) / "shareable_report.html"
        target.write_text(share_html, encoding="utf-8")
        st.success(
            f"Shareable report: {target.name} ({target.stat().st_size:,} bytes, no external assets)."
        )
        st.download_button(
            "Download shareable report",
            share_html.encode("utf-8"),
            file_name=target.name,
            mime="text/html",
        )

        st.divider()
        contracts = available_contracts()
        if contracts:
            contract_name = st.selectbox("Data contract", contracts, key="contract_choice")
            try:
                outcome = check_contract(bundle["clean"], contract_name)
                if outcome.passed:
                    st.success(
                        f"{contract_name}: passed — {outcome.rows_checked} rows, "
                        f"{outcome.fields_checked} fields checked."
                    )
                else:
                    st.error(
                        f"{contract_name}: {len(outcome.failures)} violation(s) across "
                        f"{outcome.rows_checked} rows, {outcome.fields_checked} fields."
                    )
                st.html(render_contract_html(outcome))
            except ContractError as exc:
                st.error(str(exc))
        else:
            st.info("No contracts found in app_files/contracts/.")
    else:
        st.info("Upload a file to share it and check it against a contract.")

# ------------------------------------------------ 14. intelligence
with _tabs[13]:
    _uploaded, _crm = _source_controls(prefix="intel")
    st.subheader("Intelligence")
    st.caption(
        "Natural-language rules and queries, ranked suggestions, and drift "
        "detection against the previous run of the same file."
    )
    bundle = _ensure_result(_uploaded, _crm)
    if bundle:
        clean = bundle["clean"]

        st.markdown("**Suggestions from your data**")
        suggestion_set = suggest(clean)
        st.html(render_suggestions_html(suggestion_set))

        st.divider()
        st.markdown("**Ask a question in plain English**")
        question = st.text_input(
            "Question",
            value="show me rows where the email is invalid",
            key="intel_question",
        )
        if question:
            result = nl_query.query(question, clean)
            if result.understood:
                st.success(
                    f"{result.matched} of {result.total} rows match. {result.explanation}"
                )
                if result.matched:
                    show(result.frame, use_container_width=True)
            else:
                st.warning(result.reason or "That request was not understood.")

        st.divider()
        st.markdown("**Build a rule instead of writing YAML**")
        st.caption(
            "The visual rule builder turns dropdowns into the same rules the "
            "engine runs — no YAML, no pattern syntax, no network call."
        )
        st.page_link(
            "pages/rule_builder_page.py",
            label="Open the rule builder",
            icon="✅",
        )
        st.page_link(
            "pages/distribution_page.py",
            label="Open cloud connectors and the hosted audit",
            icon="🚚",
        )

        st.divider()
        st.markdown("**Anomaly check against the previous run**")
        st.caption("The first check records a baseline; later checks compare against it.")
        if st.button("Check for anomalies"):
            report = detect(clean, name=f"utility_{_crm}", quality_score=bundle["profile"].overall)
            if report.is_baseline_run:
                st.info("Baseline recorded. Run the same check after your next import to see drift.")
            else:
                st.html(render_anomaly_html(report))
        if st.button("Clear baselines"):
            removed = clear_baselines()
            st.success(f"Removed {removed} stored baseline(s).")
    else:
        st.info("Upload a file to use the intelligence tools.")