"""Route ``/settings`` — licence status and where things live on disk.

The activation path is deliberately a paste-in text box: the buyer receives a
JSON licence by email, and asking them to find and create a hidden config
directory by hand is the step where a $2,000 sale turns into a support email.
"""

from __future__ import annotations

import json

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import (
    config_home,
    current_mode,
    license_path,
    verify_license,
    write_license,
)

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
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
                ui.label(licence.reason or "").classes("text-sm text-gray-500")
            c.metric_row(
                [
                    (limits.max_rows or "unlimited", "Row limit"),
                    (f"{limits.max_file_size_mb:g} MB" if limits.max_file_size_mb else "unlimited",
                     "File size limit"),
                    (", ".join(limits.output_formats).upper(), "Output formats"),
                    ("Off", "Lineage / Batch / Branding"),
                ]
            )

        c.section("Activate a licence", "Paste the licence JSON you were sent.")
        licence_box = ui.textarea(
            "Licence JSON",
            placeholder='{"email": "...", "issued": "2025-01-01", "signature": "..."}',
        ).classes("w-full").props("outlined")

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

        ui.button("Activate", on_click=activate).props("unelevated no-caps").mark(
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
                ui.label(value).classes("text-sm text-gray-500 font-mono")

        c.section("Feature set")
        c.file_table(
            _feature_frame(limits),
            columns=["feature", "state"],
            limit=20,
        )


def _feature_frame(limits):
    import pandas as pd

    features = [
        ("Unlimited rows", not limits.max_rows),
        ("Unlimited file size", not limits.max_file_size_mb),
        ("All output formats", len(limits.output_formats) > 1),
        ("No watermark", not limits.watermark),
        ("Row-level lineage", limits.lineage),
        ("Batch folder processing", limits.batch),
        ("White-label branding", limits.branding),
    ]
    return pd.DataFrame(
        [
            {"feature": name, "state": "Included" if included else "Demo only"}
            for name, included in features
        ]
    )