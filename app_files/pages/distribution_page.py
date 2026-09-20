"""Distribution page — cloud connectors and the hosted audit service.

LAYER 11 became real code but had no front door: the connectors authenticate and
pull files, and the hosted-audit engine prices, pays and audits an upload, yet
nothing a buyer could click reached either. This page is that front door.

Two tabs:

* **Cloud connectors** — pick a provider, see exactly which credential
  environment variables it needs, and pull a file. When credentials are absent
  the page names the missing variable instead of failing obscurely. The offline
  demo injects a canned response, which proves the request is built and the
  response parsed without a network call or a credential — the same technique
  the connector tests use.
* **Hosted audit** — the "upload, pay, get a report" product. Quotes the tier
  from the real file size, runs the same audit the installed tool runs, and
  writes a standalone HTML report. With no ``STRIPE_API_KEY`` the page says so
  and uses the stub provider, which is honest about being demo-only.

This imports the distribution layer for use only; nothing here modifies it.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app_files.distribution.connectors import (
    ConnectorError,
    MissingCredentials,
    available_connectors,
    credential_report,
    get_connector,
)
from app_files.distribution.hosted_audit import (
    Order,
    orders_frame,
    payment_is_wired,
    pricing_for,
    process_order,
)

st.set_page_config(page_title="Distribution", page_icon="🚚", layout="wide")
st.title("Distribution")
st.caption(
    "Pull files straight from cloud storage, and offer a hosted audit to "
    "buyers who would rather not install anything."
)

_DEMO_BODY = b"email,phone\nada@example.com,+14155550100\ngrace@example.com,\n"

# The offline demo needs credentials present, because its point is to exercise
# the request path, not the missing-credential path.
_DEMO_ENVIRON = {
    "GOOGLE_ACCESS_TOKEN": "demo-token",
    "DROPBOX_ACCESS_TOKEN": "demo-token",
    "MS_GRAPH_ACCESS_TOKEN": "demo-token",
}


class _DemoResponse:
    """The slice of an HTTP response the connectors actually touch."""

    def __init__(self, payload: Any, body: bytes = b"", content_type: str = "text/csv") -> None:
        self._payload = payload
        self.content = body
        self.status_code = 200
        self.headers = {"Content-Type": content_type}

    def json(self) -> Any:
        return self._payload


def _demo_transport(provider: str):
    """A transport that replays a canned provider response."""

    def transport(method: str, url: str, **kwargs: Any) -> _DemoResponse:
        if provider == "google_sheets":
            return _DemoResponse({"values": [["email", "phone"], ["ada@example.com", "+14155550100"]]})
        return _DemoResponse(None, _DEMO_BODY)

    return transport


class _DemoS3Client:
    """The slice of a boto3 client the S3 connector touches."""

    def get_object(self, Bucket: str, Key: str) -> dict[str, Any]:  # noqa: N803 - boto3 casing
        import io as _io

        return {"Body": _io.BytesIO(_DEMO_BODY), "ContentType": "text/csv"}


connector_tab, audit_tab = st.tabs(["Cloud connectors", "Hosted audit"])


# ------------------------------------------------------------------ connectors
with connector_tab:
    st.subheader("Pull a file from cloud storage")
    st.caption(
        "Credentials are read from environment variables. This page never asks "
        "you to paste a secret into a form, and never writes one to disk."
    )

    st.markdown("**Credential status**")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "provider": entry["provider"],
                    "ready": "yes" if entry["ready"] else "no",
                    "missing": ", ".join(entry["missing"]) or "—",
                }
                for entry in credential_report()
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    providers = available_connectors()
    provider = st.selectbox("Provider", providers, format_func=str.title)

    fields: dict[str, str] = {}
    if provider == "s3":
        fields["bucket"] = st.text_input("Bucket", value="demo-bucket")
        fields["key"] = st.text_input("Object key", value="contacts.csv")
    elif provider == "google_sheets":
        fields["spreadsheet_id"] = st.text_input("Spreadsheet ID", value="demo-sheet-id")
        fields["sheet_name"] = st.text_input("Sheet name", value="Sheet1")
    elif provider == "google_drive":
        fields["file_id"] = st.text_input("File ID", value="demo-file-id")
    elif provider == "dropbox":
        fields["path"] = st.text_input("Path", value="/Clients/Acme/contacts.csv")
    elif provider == "onedrive":
        fields["item_path"] = st.text_input("Item path", value="Clients/Acme/contacts.csv")

    use_demo = st.checkbox(
        "Use the offline demo response",
        value=True,
        help=(
            "Serves a canned provider response instead of calling the provider. "
            "Proves the request is built and the response parsed, without a "
            "network call or a credential."
        ),
    )

    if st.button("Pull file", type="primary"):
        try:
            if use_demo:
                extra: dict[str, Any] = {
                    "environ": _DEMO_ENVIRON,
                    "transport": _demo_transport(provider),
                }
                if provider == "s3":
                    extra["client"] = _DemoS3Client()
                connector = get_connector(provider, **{**fields, **extra})
            else:
                connector = get_connector(provider, **fields)

            status = connector.check_credentials()
            if not status["ready"] and not use_demo:
                st.warning(
                    "Missing credentials: "
                    + ", ".join(status["missing"])
                    + ". Set them in the environment and try again."
                )
            else:
                fetched = connector.fetch()
                st.success(f"Pulled `{fetched.name}` ({len(fetched.data):,} bytes).")
                st.download_button(
                    "Download pulled file",
                    fetched.data,
                    file_name=fetched.name,
                    mime=fetched.content_type or "application/octet-stream",
                )
        except MissingCredentials as exc:
            st.error(f"Not configured: {exc}")
        except ConnectorError as exc:
            st.error(f"Could not pull that file: {exc}")
        except Exception as exc:  # noqa: BLE001 - the page must never crash
            st.error(f"Unexpected error: {exc}")


# ------------------------------------------------------------------ hosted audit
with audit_tab:
    st.subheader("Hosted audit — upload, pay, download the report")
    st.caption(
        "For buyers who want the result without installing anything. The audit "
        "is the same profiling the installed tool runs, so the numbers match."
    )

    if payment_is_wired().get("live_payments"):
        st.success("Live payments are configured.")
    else:
        st.warning(
            "No `STRIPE_API_KEY` is set, so this runs the demo payment provider. "
            "Orders are recorded and paid immediately; no money changes hands."
        )

    upload = st.file_uploader("File to audit", type=["csv", "tsv", "txt", "json", "xlsx", "pdf"])
    email = st.text_input("Email for the report", value="")

    if upload is not None:
        size = len(upload.getvalue())
        quote = pricing_for(size)
        left, middle, right = st.columns(3)
        left.metric("File size", f"{size / 1024:,.1f} KB")
        middle.metric("Tier", quote["tier"])
        right.metric("Price", f"{quote['currency']} {quote['price']}")

        if st.button("Submit order", type="primary"):
            order = Order.create(upload.name, size, email=email)
            result = process_order(order, upload.getvalue())
            summary = result.get("summary")
            if summary is None:
                st.info(result.get("message", "Order recorded."))
            else:
                st.success(result["message"])
                metrics = st.columns(4)
                metrics[0].metric("Rows", summary["rows"])
                metrics[1].metric("Columns", summary["columns"])
                metrics[2].metric("Quality score", f"{summary['quality_score']}%")
                metrics[3].metric("Order", order.order_id)
                report_path = Path(result["report_path"])
                st.download_button(
                    "Download audit report (HTML)",
                    report_path.read_bytes(),
                    file_name=report_path.name,
                    mime="text/html",
                )

    st.divider()
    st.markdown("**Recent orders**")
    frame = orders_frame()
    if frame.empty:
        st.info("No orders yet.")
    else:
        st.dataframe(frame, use_container_width=True, hide_index=True)