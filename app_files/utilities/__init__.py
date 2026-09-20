"""The utility suite: the features a buyer lists when describing the tool.

Ten small, independently useful capabilities built on top of the frozen core:

* data quality score      — one number, with the rows that dragged it down
* "what was fixed"        — one plain-English paragraph per run
* before/after diff       — side-by-side HTML with changes highlighted
* lineage explorer        — every transformation, searchable (see ``app_files.lineage``)
* reconciliation dashboard— matched / missing / never cleared / variance
* template marketplace    — browse and install template packs
* sample data generator   — messy test data for any schema
* export to any format    — csv, excel, json, sql, pdf, html
* client workspaces       — one folder per client (see ``app_files.collaboration``)
* audit trail             — hashed record of every run (see ``app_files.collaboration``)

Everything here calls into the frozen core; nothing modifies it.
"""

from app_files.utilities.exports import (
    EXTENDED_FORMATS,
    available_formats,
    render_dashboard_html,
    write_any_extended,
    write_html,
    write_pdf,
)
from app_files.utilities.fix_summary import (
    FixSummary,
    render_summary_html,
    render_summary_markdown,
    summary_frame,
    write_summary,
)
from app_files.utilities.marketplace import (
    CatalogEntry,
    InstallError,
    catalog,
    catalog_frame,
    install_from_folder,
    install_from_zip,
    marketplace_summary,
    uninstall,
)
from app_files.utilities.reconciliation_dashboard import (
    Dashboard,
    ReconciliationSummary,
    build_dashboard,
    dashboard_frame,
    write_dashboard_html,
)
from app_files.utilities.rule_library import (
    RuleSet,
    available_rule_sets,
    get_rule_set,
    install,
    load_library,
    rule_library_frame,
    validate_many,
    validate_rule_set,
)
from app_files.utilities.sample_generator import (
    Field,
    Profile,
    available_profiles,
    corrupt,
    generate,
    generate_bytes,
    generate_csv,
    schema_description,
)

__all__ = [
    "CatalogEntry",
    "Dashboard",
    "EXTENDED_FORMATS",
    "Field",
    "FixSummary",
    "InstallError",
    "Profile",
    "ReconciliationSummary",
    "RuleSet",
    "available_formats",
    "available_profiles",
    "available_rule_sets",
    "build_dashboard",
    "catalog",
    "catalog_frame",
    "corrupt",
    "dashboard_frame",
    "generate",
    "generate_bytes",
    "generate_csv",
    "get_rule_set",
    "install",
    "install_from_folder",
    "install_from_zip",
    "load_library",
    "marketplace_summary",
    "render_dashboard_html",
    "render_summary_html",
    "render_summary_markdown",
    "rule_library_frame",
    "schema_description",
    "summary_frame",
    "uninstall",
    "validate_many",
    "validate_rule_set",
    "write_any_extended",
    "write_dashboard_html",
    "write_html",
    "write_pdf",
    "write_summary",
]