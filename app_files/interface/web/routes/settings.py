"""Route ``/settings`` — licence status and where things live on disk.

The activation path is deliberately a paste-in text box: the buyer receives a
JSON licence by email, and asking them to find and create a hidden config
directory by hand is the step where a $2,000 sale turns into a support email.
"""

from __future__ import annotations

import json

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import (
    config_home,
    current_mode,
    license_path,
    verify_license,
    write_license,
)
from app_files.settings import purchase_url

NAV = [
    ("Home", "/demo"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
    ("Verify", "/verify"),
]


@ui.page("/settings")
def settings_page() -> None:
    theme.inject_theme()
    licence, limits = current_mode()

    with page_shell(NAV, active="/settings"):
        c.page_header("Settings", "Licence status, feature set and file locations.")

        c.section("Licence")
        if licence.valid:
            c.metric_row(
                [
                    (licence.email or "—", "Licensed to"),
                    (licence.issued or "—", "Issued"),
                    (licence.version or "—", "Version"),
                    ("Full", "Mode"),
                ]
            )
        else:
            with ui.row().classes("items-center gap-2"):
                c.demo_badge("Demo mode")
                ui.label(licence.reason or "").classes("text-sm").style(
                    f"color:{theme.SLATE}"
                )
            # The demo panel states what the demo actually grants. The run
            # allowance is shown live, and the other rows name the feature set
            # rather than a cap, because the demo does not cap them.
            remaining = session_store.runs_remaining(limits.max_runs_per_session)
            c.metric_row(
                [
                    (remaining if remaining is not None else "—", "Runs remaining this session"),
                    ("No limit", "File size"),
                    ("CSV · Excel · JSON · SQL", "Output formats"),
                    ("Enabled", "Lineage · Batch · Branding"),
                ]
            )
            c.purchase_note(purchase_url())

        c.section("Activate a licence", "Paste the licence JSON you were sent.")
        licence_box = c.textarea(
            "Licence JSON",
            placeholder='{"email": "...", "issued": "2025-01-01", "signature": "..."}',
        )

        def activate() -> None:
            raw = (licence_box.value or "").strip()
            if not raw:
                ui.notify("Paste a licence first.", type="warning")
                return
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                ui.notify(f"That is not valid JSON: {exc}", type="negative", multi_line=True)
                return
            verified = verify_license(data)
            if not verified.valid:
                ui.notify(
                    verified.reason or "That licence is not valid.",
                    type="negative",
                    multi_line=True,
                )
                return
            path = write_license(data)
            ui.notify(f"Licence activated. Saved to {path}", type="positive")
            ui.navigate.to("/settings")

        theme.button("Activate", on_click=activate).mark(
            "activate-licence"
        )

        c.section("Locations")
        rows = [
            ("Config directory", str(config_home())),
            ("Licence file", str(license_path())),
            ("Branding file", str(config_home() / "branding.json")),
        ]
        for label, value in rows:
            with ui.row().classes("items-center gap-3"):
                ui.label(label).classes("text-sm font-medium w-40")
                ui.label(value).classes("text-sm font-mono").style(f"color:{theme.SLATE}")

        c.section("Feature set")
        c.file_table(
            _feature_frame(limits),
            columns=["feature", "state"],
            limit=20,
        )


def _feature_frame(limits):
    import pandas as pd

    features = [
        ("Unlimited rows", limits.max_rows is None),
        ("Unlimited file size", limits.max_file_size_mb is None),
        ("All output formats", len(limits.output_formats) > 1),
        ("No watermark", not limits.watermark),
        ("Row-level lineage", limits.lineage),
        ("Batch folder processing", limits.batch),
        ("White-label branding", limits.branding),
        (
            "Unlimited runs",
            limits.max_runs_per_session is None,
        ),
    ]
    return pd.DataFrame(
        [
            {"feature": name, "state": "Included" if included else "Demo only"}
            for name, included in features
        ]
    )