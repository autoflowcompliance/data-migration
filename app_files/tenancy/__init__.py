"""Layer 16 — multi-tenancy and cloud.

A tenant is the unit of isolation: its own data, config, outputs, queue and
license, under one root. The existing ``collaboration.workspaces`` treats a
client the same way, so a tenant does not replace it — a tenant *contains*
workspaces and adds the things a hosted install needs around them: a stable
tenant id separate from a display name, a license binding, a backup and restore
path, and an isolation guarantee that can be asserted rather than assumed.

Two invariants the tests pin:

* **No data crosses.** Every path a tenant hands back is rooted inside its own
  root, and ``resolve_path`` refuses ``..``. Two tenants with the same client
  name still get different folders, because the folder is keyed on the tenant
  id, not the name.
* **A restore is verifiable.** ``Backup`` records a digest per file; ``restore``
  checks every digest and reports a mismatch instead of silently writing a
  corrupt tree. A backup you cannot verify is not a backup.

``AUTOFLOW_HOME`` relocates the tenants root, matching every other stateful
layer, so a desktop install does not write beside the code.
"""

from __future__ import annotations

from app_files.tenancy.backup import (
    Backup,
    BackupError,
    BackupManifest,
    RestoreReport,
    create_backup,
    restore_backup,
    verify_backup,
)
from app_files.tenancy.deploy import (
    DEPLOY_TARGETS,
    DeploymentPlan,
    deploy_manifest,
    deployment_plan,
)
from app_files.tenancy.tenants import (
    Tenant,
    TenantError,
    TenantRegistry,
    ensure_tenant,
    get_tenant,
    list_tenants,
    tenants_dir,
)

__all__ = [
    "DEPLOY_TARGETS",
    "Backup",
    "BackupError",
    "BackupManifest",
    "DeploymentPlan",
    "RestoreReport",
    "Tenant",
    "TenantError",
    "TenantRegistry",
    "create_backup",
    "deploy_manifest",
    "deployment_plan",
    "ensure_tenant",
    "get_tenant",
    "list_tenants",
    "restore_backup",
    "tenants_dir",
    "verify_backup",
]
