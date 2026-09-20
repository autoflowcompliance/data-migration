"""Route ``/branding`` — logo, company name and accent colour for reports.

Branding is a licensed feature. The settings file can still be written without
one (an agency preparing a client folder in advance), but the page says plainly
that it will not be applied.

Uploaded logos are stored under the DataReady config directory rather than in
the source tree, so an installed client never needs write access to its own
program files.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from app_files.branding import Branding, load_branding, save_branding
from app_files.interface.web import components as c
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import config_home, current_mode

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Branding", "/branding"),
    ("Settings", "/settings"),
]


def assets_dir() -> Path:
    return config_home() / "assets"


@ui.page("/branding")
def branding_page() -> None:
    theme.inject_theme()
    _licence, limits = current_mode()
    branding = load_branding()

    with page_shell(NAV, active="/branding"):
        c.page_header(
            "White-label branding",
            "Put your own company name and logo on every report you deliver.",
        )

        if not limits.branding:
            ui.html(
                '<div class="dr-trust">Branding is a licensed feature. Settings saved '
                "here will be applied as soon as a licence is installed.</div>"
            )

        company = ui.input("Company name", value=branding.company_name).classes(
            "w-full"
        ).props("outlined dense")
        email = ui.input("Contact email", value=branding.contact_email or "").classes(
            "w-full"
        ).props("outlined dense")
        website = ui.input("Website", value=branding.website or "").classes(
            "w-full"
        ).props("outlined dense")
        accent = ui.input("Accent colour", value=branding.accent_color).classes(
            "w-48"
        ).props("outlined dense")
        powered = ui.switch("Show 'Powered by DataReady'", value=branding.show_powered_by)

        c.section("Logo")
        logo_label = ui.label(
            branding.logo_path or "No logo uploaded yet."
        ).classes("text-sm text-gray-500")
        upload_path = {"path": branding.logo_path}

        has_logo = bool(branding.logo_path) and Path(branding.logo_path or "").is_file()
        preview = ui.image().classes("max-h-16")
        if has_logo:
            preview.set_source(branding.logo_path)
        preview.set_visibility(has_logo)

        def handle_logo(event) -> None:
            destination_dir = assets_dir()
            destination_dir.mkdir(parents=True, exist_ok=True)
            suffix = Path(event.name).suffix.lower() or ".png"
            destination = destination_dir / f"brand_logo{suffix}"
            destination.write_bytes(event.content.read())
            upload_path["path"] = str(destination)
            logo_label.text = str(destination)
            preview.set_source(destination)
            preview.set_visibility(True)

        ui.upload(
            on_upload=handle_logo,
            auto_upload=True,
            label="Upload a logo (PNG, JPG or SVG)",
            max_file_size=2_000_000,
        ).classes("w-full")

        def save() -> None:
            updated = Branding(
                company_name=company.value or "DataReady",
                logo_path=upload_path["path"],
                contact_email=email.value or None,
                website=website.value or None,
                accent_color=accent.value,
                show_powered_by=bool(powered.value),
            )
            path = save_branding(updated)
            ui.notify(f"Saved to {path}", type="positive")

        def reset() -> None:
            save_branding(Branding())
            ui.notify("Reset to the default branding.", type="info")
            ui.navigate.to("/branding")

        with ui.row().classes("gap-3 mt-2"):
            ui.button("Save branding", on_click=save).props("unelevated no-caps")
            ui.button("Reset to default", on_click=reset).props("outline no-caps")

        c.section("Where this appears")
        ui.label(
            "The company name, logo, contact details and accent colour are "
            "substituted into every QA report and batch dashboard at render time."
        ).classes("text-sm text-gray-500")