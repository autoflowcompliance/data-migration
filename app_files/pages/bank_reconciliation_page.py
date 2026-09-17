"""Bank Reconciliation & Cleanup — Streamlit page.

Lives in app_files/pages/, so it appears as a separate page in Streamlit's
native sidebar navigation automatically. This file is completely independent
of app.py and admin.py — nothing here can break the CRM migration tool,
and nothing in the CRM tool can break this.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.bank_reconciliation.reconciler import run_reconciliation

st.set_page_config(page_title="Bank Reconciliation", page_icon="◆", layout="wide")

st.html(
    """
    <div style="background:#14181F; border-radius:10px; padding:24px 28px; margin-bottom:16px;">
        <div style="color:#F7F6F3; font-size:1.3rem; font-weight:600;">Bank Reconciliation &amp; Cleanup</div>
        <div style="color:#AEB6C2; font-size:.92rem; margin-top:4px;">
            Match a bank statement against your own ledger and find every discrepancy.
        </div>
    </div>
    """
)

st.html(
    """
    <div style="display:flex; gap:10px; background:#FFFFFF; border:1px solid #DDD9D0;
                border-left:3px solid #1F9E8B; border-radius:6px; padding:12px 16px;
                margin-bottom:20px; font-size:.88rem; color:#5B6472;">
        <span>&#8505;&#65039;</span>
        <div><b>This is prep work, not finished bookkeeping.</b> This tool finds and cleans
        mismatches &mdash; it does not categorize transactions or make accounting judgments.
        Hand the results to your bookkeeper or accountant to finalize.</div>
    </div>
    """
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Bank statement")
    bank_file = st.file_uploader("Upload your bank statement CSV", type=["csv"], key="bank")
    bank_date_col = st.text_input("Date column name", value="Date", key="bank_date")
    bank_amount_col = st.text_input("Amount column name", value="Amount", key="bank_amount")

with col2:
    st.subheader("Your ledger / books")
    ledger_file = st.file_uploader("Upload your ledger export CSV", type=["csv"], key="ledger")
    ledger_date_col = st.text_input("Date column name", value="Date", key="ledger_date")
    ledger_amount_col = st.text_input("Amount column name", value="Amount", key="ledger_amount")

date_tolerance = st.slider(
    "Date matching tolerance (days)", min_value=0, max_value=7, value=2,
    help="Bank clearing dates often differ slightly from ledger entry dates.",
)

run_clicked = st.button("Run reconciliation", type="primary", disabled=not (bank_file and ledger_file))

if run_clicked and bank_file and ledger_file:
    try:
        with st.spinner("Cleaning and matching transactions..."):
            result = run_reconciliation(
                bank_file.getvalue(), ledger_file.getvalue(),
                bank_date_col, bank_amount_col, ledger_date_col, ledger_amount_col,
                date_tolerance,
            )
        summary = result["summary"]

        st.success(
            f"Done — {summary['matched']} matched, "
            f"{summary['missing_from_books']} missing from your books, "
            f"{summary['recorded_but_never_cleared']} recorded but never cleared."
        )

        cols = st.columns(5)
        cols[0].metric("Bank transactions", summary["bank_transactions"])
        cols[1].metric("Ledger transactions", summary["ledger_transactions"])
        cols[2].metric("Matched", summary["matched"])
        cols[3].metric("Missing from books", summary["missing_from_books"])
        cols[4].metric("Never cleared", summary["recorded_but_never_cleared"])

        tabs = st.tabs(["Missing from your books", "Recorded but never cleared", "Matched transactions"])
        with tabs[0]:
            st.caption("These showed up in your bank statement but aren't in your books yet.")
            st.dataframe(result["bank_only"], use_container_width=True)
            st.download_button(
                "Download CSV", result["bank_only"].to_csv(index=False),
                file_name="missing_from_your_books.csv", mime="text/csv",
            )
        with tabs[1]:
            st.caption("These are in your books but never actually cleared the bank — worth double-checking.")
            st.dataframe(result["ledger_only"], use_container_width=True)
            st.download_button(
                "Download CSV", result["ledger_only"].to_csv(index=False),
                file_name="recorded_but_never_cleared.csv", mime="text/csv",
            )
        with tabs[2]:
            import pandas as pd
            st.dataframe(pd.DataFrame(result["matches"]), use_container_width=True)

    except KeyError as e:
        st.error(f"Column not found: {e}. Check the column names match your file's actual headers.")
    except Exception as e:
        st.error("Something went wrong processing these files.")
        st.caption(f"Technical details: {str(e)}")
elif not (bank_file and ledger_file):
    st.caption("Upload both files above to run the reconciliation.")
