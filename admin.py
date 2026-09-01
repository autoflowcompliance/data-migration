"""Admin CLI — Private Client Delivery System (no UI framework).

Run locally: python admin.py
Menu-driven: process jobs, run post-import audits, and review your order
history, all through numbered prompts — no browser required.
"""
from __future__ import annotations

import datetime
import re
import sys
import zipfile
import io
from pathlib import Path

import chardet
import pandas as pd

from app_files.auditors import audit_import
from app_files.cleaners import CleaningConfig
from app_files.mappers import available_crms
from app_files.pipeline import run_pipeline
from app_files.reporters import render_audit_report

BASE_DIR = Path(__file__).resolve().parent
DELIVERIES_DIR = BASE_DIR / "deliveries"
ORDERS_LOG = BASE_DIR / "orders_log.csv"
DELIVERIES_DIR.mkdir(exist_ok=True)

LOG_COLUMNS = [
    "timestamp", "client_name", "client_email", "tier", "price",
    "target_crm", "rows_in", "rows_out", "quality_score", "errors",
    "warnings", "guarantee_met", "zip_filename",
]

TIER_PRICING = {
    "1": ("Starter", 600, "< 1,000 rows"),
    "2": ("Standard", 1500, "1,000-10,000 rows"),
    "3": ("Premium", 2000, "10,000+ rows"),
}

TIER_DELIVERABLES = {
    "Starter": {"clean_csv"},
    "Standard": {"clean_csv", "mapping_log", "cleaning_log", "issues", "qa_report"},
    "Premium": {"clean_csv", "mapping_log", "cleaning_log", "issues", "qa_report"},
}

GUARANTEE_MAX_ERRORS = 0  # errors above this = flag before sending


# --------------------------------------------------------------------------
# Small prompt helpers — this is the "interface" layer, replacing widgets
# --------------------------------------------------------------------------
def prompt_text(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def prompt_yes_no(label: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    value = input(f"{label} {suffix}: ").strip().lower()
    if not value:
        return default
    return value.startswith("y")


def prompt_choice(label: str, options: dict[str, tuple]) -> str:
    print(f"\n{label}")
    for key, val in options.items():
        print(f"  {key}) {val[0]} — {val[1]}" if len(val) > 1 else f"  {key}) {val[0]}")
    while True:
        choice = input("Select: ").strip()
        if choice in options:
            return choice
        print("Invalid option, try again.")


def prompt_list_choice(label: str, options: list[str]) -> str:
    print(f"\n{label}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        choice = input("Select: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid option, try again.")


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", name).strip("_") or "client"


def append_order_log(row: dict) -> None:
    df_row = pd.DataFrame([row], columns=LOG_COLUMNS)
    if ORDERS_LOG.exists():
        df_row.to_csv(ORDERS_LOG, mode="a", header=False, index=False)
    else:
        df_row.to_csv(ORDERS_LOG, mode="w", header=True, index=False)


def read_csv_file(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    if not raw:
        raise ValueError("File is empty.")
    encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)


# --------------------------------------------------------------------------
# Menu 1 — Process a new job
# --------------------------------------------------------------------------
def process_new_job() -> None:
    print("\n=== Process a new job ===")
    csv_path = Path(prompt_text("Path to client's CSV file"))
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    try:
        source = read_csv_file(csv_path)
    except Exception as e:
        print(f"Could not read file: {e}")
        return
    print(f"Loaded: {len(source)} rows, {len(source.columns)} columns.")

    client_name = prompt_text("Client / project name")
    if not client_name:
        print("Client name is required.")
        return
    client_email = prompt_text("Client email")

    tier_key = prompt_choice(
        "Package tier:",
        {k: (v[0], f"${v[1]} — {v[2]}") for k, v in TIER_PRICING.items()},
    )
    tier, suggested_price, _ = TIER_PRICING[tier_key]
    price_input = prompt_text(f"Price ($, default {suggested_price})", str(suggested_price))
    price = int(price_input) if price_input.isdigit() else suggested_price

    if tier == "Starter" and len(source) >= 1000:
        print(f"Note: this file has {len(source)} rows — outside the Starter range. Consider re-pricing.")
    elif tier == "Standard" and len(source) >= 10000:
        print(f"Note: this file has {len(source)} rows — Premium range. Consider re-pricing.")

    target_crm = prompt_list_choice("Target CRM:", available_crms())

    use_defaults = prompt_yes_no("Use default cleaning settings (recommended)?", default=True)
    if use_defaults:
        remove_duplicates = standardize_dates = standardize_phones = fix_scientific = True
        normalize_unicode = False
        missing_strategy = "flag"
        region = "US"
        date_first = False
    else:
        remove_duplicates = prompt_yes_no("Remove duplicates?", True)
        standardize_dates = prompt_yes_no("Standardize dates?", True)
        date_first = prompt_yes_no("Parse dates day-first (DD/MM/YYYY)?", False)
        standardize_phones = prompt_yes_no("Standardize phones (E.164)?", True)
        fix_scientific = prompt_yes_no("Fix Excel scientific notation?", True)
        normalize_unicode = prompt_yes_no("Fold accents to ASCII?", False)
        missing_strategy = prompt_list_choice("Missing values strategy:", ["flag", "auto", "drop"])
        region = prompt_text("Phone region", "US")

    brand_name = prompt_text("Brand name (for reports)", "AutoFlow")
    tool_name = prompt_text("Tool name (for reports)", "Data Migration Tool")

    print("\nRunning pipeline…")
    try:
        import os
        os.environ["BRAND_NAME"] = brand_name
        os.environ["TOOL_NAME"] = tool_name

        result = run_pipeline(
            source=source,
            crm=target_crm,
            cleaning_config=CleaningConfig(
                remove_duplicates=remove_duplicates,
                standardize_dates=standardize_dates,
                date_first=date_first,
                standardize_phones=standardize_phones,
                fix_scientific_notation=fix_scientific,
                normalize_unicode=normalize_unicode,
                missing_value_strategy=missing_strategy,
                default_region=region.upper() or "US",
            ),
            project_name=client_name,
            source_filename=csv_path.name,
        )
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return

    summary = result.summary()
    guarantee_met = summary["errors"] <= GUARANTEE_MAX_ERRORS

    print("\n--- Delivery summary ---")
    print(f"Quality score:      {summary['quality_score']}%")
    print(f"Records out:        {summary['rows_out']}")
    print(f"Duplicates removed: {summary['duplicates_removed']}")
    print(f"Errors:             {summary['errors']}")
    print(f"Warnings:           {summary['warnings']}")

    if guarantee_met:
        print("\n✅ Meets your delivery guarantee (no unresolved errors). Safe to send.")
    else:
        print(f"\n⚠️  {summary['errors']} unresolved error(s) — this does NOT meet your guarantee. "
              f"Review before sending anything to the client.")
        issues = result.validation.issues_frame()
        if not issues.empty:
            print(issues.head(10).to_string())
        if not prompt_yes_no("Package and save anyway?", default=False):
            print("Cancelled — nothing saved.")
            return

    include = TIER_DELIVERABLES[tier]
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        if "clean_csv" in include:
            zf.writestr("clean_data.csv", result.clean_frame.to_csv(index=False))
        if "mapping_log" in include:
            zf.writestr("mapping_log.csv", result.mapping_log().to_csv(index=False))
        if "cleaning_log" in include:
            zf.writestr("cleaning_log.csv", result.cleaning_log().to_csv(index=False))
        if "issues" in include:
            zf.writestr("issues.csv", result.validation.issues_frame().to_csv(index=False))
        if "qa_report" in include:
            zf.writestr("qa_report.html", result.qa_report_html)

    safe_client = sanitize_filename(client_name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{safe_client}_{target_crm}_{timestamp}.zip"
    archive_path = DELIVERIES_DIR / zip_filename
    archive_path.write_bytes(zip_buffer.getvalue())

    append_order_log({
        "timestamp": timestamp,
        "client_name": client_name,
        "client_email": client_email,
        "tier": tier,
        "price": price,
        "target_crm": target_crm,
        "rows_in": summary["rows_in"],
        "rows_out": summary["rows_out"],
        "quality_score": summary["quality_score"],
        "errors": summary["errors"],
        "warnings": summary["warnings"],
        "guarantee_met": guarantee_met,
        "zip_filename": zip_filename,
    })

    print(f"\nSaved to: {archive_path}")
    print("Logged in orders_log.csv. Ready to send to the client.")


# --------------------------------------------------------------------------
# Menu 2 — Post-import audit
# --------------------------------------------------------------------------
def run_audit_flow() -> None:
    print("\n=== Post-import audit ===")
    project_name = prompt_text("Client / project name (for the report)")
    expected_path = Path(prompt_text("Path to the clean_data.csv you delivered"))
    exported_path = Path(prompt_text("Path to the client's fresh CRM export"))
    key_column = prompt_text("Unique key column present in both files", "email")

    if not expected_path.exists() or not exported_path.exists():
        print("One or both files not found.")
        return

    try:
        expected_df = pd.read_csv(expected_path, dtype=str, keep_default_na=False)
        exported_df = pd.read_csv(exported_path, dtype=str, keep_default_na=False)
        audit = audit_import(expected=expected_df, exported=exported_df, key=key_column)
    except Exception as e:
        print(f"Audit failed — check both files share the key column. Error: {e}")
        return

    print("\n--- Audit results ---")
    for k, v in audit.stats().items():
        print(f"{k}: {v}")
    if not audit.mismatches.empty:
        print("\nMismatches:")
        print(audit.mismatches.head(15).to_string())

    report_html = render_audit_report(audit.stats(), audit.mismatches, project_name or "Project")
    out_path = DELIVERIES_DIR / f"{sanitize_filename(project_name or 'audit')}_audit_report.html"
    out_path.write_text(report_html)
    print(f"\nAudit report saved to: {out_path}")


# --------------------------------------------------------------------------
# Menu 3 — Job log
# --------------------------------------------------------------------------
def view_job_log() -> None:
    print("\n=== Job log ===")
    if not ORDERS_LOG.exists():
        print("No jobs processed yet.")
        return
    log_df = pd.read_csv(ORDERS_LOG)
    print(log_df.sort_values("timestamp", ascending=False).to_string(index=False))
    print(f"\n{len(log_df)} job(s) logged · stored at {ORDERS_LOG}")


# --------------------------------------------------------------------------
# Main menu loop
# --------------------------------------------------------------------------
def main() -> None:
    print("Client Job Processor — Admin (local, no row limits)")
    while True:
        print("\n==============================")
        print("1) Process a new job")
        print("2) Run post-import audit")
        print("3) View job log")
        print("4) Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            process_new_job()
        elif choice == "2":
            run_audit_flow()
        elif choice == "3":
            view_job_log()
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
