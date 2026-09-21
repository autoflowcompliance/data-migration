"""Route ``/templates`` — browse the target configs and run one against a sample.

This is the discovery page: it lists every YAML in ``app_files/configs`` with
its description and rules, and offers a sample run so a visitor can see what a
particular target system does before uploading client data.
"""

from __future__ import annotations

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import current_mode
from app_files.mappers import load_mapping_config

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
]


@ui.page("/templates")
def templates_page() -> None:
    theme.inject_theme()
    _licence, limits = current_mode()

    with page_shell(NAV, active="/templates"):
        c.page_header(
            "Templates",
            "One config per target system. Drop a new YAML in app_files/configs "
            "and it appears here with no code change.",
        )

        samples = state.available_samples()
        for name in state.templates_on_disk():
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center w-full"):
                    ui.label(name).classes("font-semibold text-lg")
                    ui.space()
                    _sample_for(name, samples, limits)

                try:
                    config = load_mapping_config(name)
                except Exception as exc:  # noqa: BLE001 - show the problem, keep the page
                    ui.label(f"This config could not be loaded: {exc}").classes(
                        "text-sm"
                    ).style(f"color:{theme.DANGER}")
                    continue

                description = _description(name)
                ui.label(
                    description or f"Maps source columns onto {config.crm} fields."
                ).classes("text-sm").style(f"color:{theme.SLATE}")

                field_names = [f.name for f in config.fields]
                ui.label(f"{len(field_names)} target field(s)").classes(
                    "text-xs"
                ).style(f"color:{theme.SLATE_LIGHT}")
                with c.expansion("Fields"):
                    ui.label(", ".join(field_names)).classes("text-sm font-mono")


def _description(template: str) -> str:
    """Read the free-text ``description:`` from a config, if it has one.

    ``MappingConfig`` is a frozen layer and does not carry this key, so the
    YAML is read directly rather than widening the frozen dataclass.
    """
    import yaml

    from app_files.mappers.schema import CONFIG_DIR

    path = CONFIG_DIR / f"{template}.yaml"
    if not path.is_file():
        return ""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return ""
    return str(data.get("description") or "").strip()


def _sample_for(template: str, samples, limits) -> None:
    """Render the 'try a sample' control for one template."""
    match = next((s for s in samples if s["template"] == template), None)
    if match is None:
        ui.label("No sample bundled").classes("text-xs").style(f"color:{theme.SLATE_LIGHT}")
        return

    def run_sample() -> None:
        outcome = state.run_migration(
            state.load_sample(match["file"]),
            source_name=match["file"],
            template=template,
            limits=limits,
        )
        session_store.set_outcome(outcome)
        ui.navigate.to("/results")

    theme.download_button(f"Try with {match['file']}", on_click=run_sample)