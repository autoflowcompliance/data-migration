"""Layer 9 — Collaboration.

Shareable reports, enforceable data contracts, per-client workspaces, and a
side-by-side comparison of what changed. Every module calls into the frozen core;
none of them modifies it.
"""

from app_files.collaboration.audit_trail import (
    AuditEntry,
    append_entry,
    build_entry,
    hash_bytes,
    hash_file,
    read_log,
    render_audit_html,
    verify_output,
    write_audit_bundle,
)
from app_files.collaboration.comparison import (
    CellChange,
    Comparison,
    RowComparison,
    build_comparison,
    changed_cell_count,
    render_comparison_html,
)
from app_files.collaboration.contracts import (
    Contract,
    ContractError,
    ContractFailure,
    ContractResult,
    available_contracts,
    check_contract,
    load_contract,
    render_contract_html,
)
from app_files.collaboration.workspaces import (
    Workspace,
    WorkspaceError,
    WorkspaceRun,
    create_workspace,
    get_workspace,
    list_workspaces,
    run_in_workspace,
)

__all__ = [
    "AuditEntry",
    "CellChange",
    "Comparison",
    "Contract",
    "ContractError",
    "ContractFailure",
    "ContractResult",
    "RowComparison",
    "Workspace",
    "WorkspaceError",
    "WorkspaceRun",
    "append_entry",
    "build_comparison",
    "build_entry",
    "changed_cell_count",
    "check_contract",
    "create_workspace",
    "get_workspace",
    "hash_bytes",
    "hash_file",
    "available_contracts",
    "list_workspaces",
    "load_contract",
    "read_log",
    "render_audit_html",
    "render_comparison_html",
    "render_contract_html",
    "run_in_workspace",
    "verify_output",
    "write_audit_bundle",
]