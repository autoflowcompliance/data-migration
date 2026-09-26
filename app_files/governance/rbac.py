"""Role-based access control.

Five roles, ordered from most to least privileged. A permission is granted to a
role, and a call out of role raises :class:`AccessDenied` rather than returning
False, because a silent no is how a viewer ends up thinking an admin action
worked.

    owner    everything, including managing other users
    admin    configure, license, audit, schedule
    operator run the pipeline, build rules and mappings, push output
    viewer   read reports and run results
    client   read only their own runs

The resource half of "permissions per role per resource" is the scope on a
:class:`Principal`: a client principal carries the workspace name it may read,
and :func:`check` refuses a cross-client read even though the role allows
reading. A role is what you may do; the scope is what you may do it to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AccessDenied(PermissionError):
    """Raised when a principal acts outside its role or its scope."""


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    CLIENT = "client"


class Permission(str, Enum):
    RUN_PIPELINE = "run_pipeline"
    READ_RESULTS = "read_results"
    READ_REPORTS = "read_reports"
    WRITE_CONFIG = "write_config"
    WRITE_RULES = "write_rules"
    PUSH_OUTPUT = "push_output"
    RECONCILE = "reconcile"
    MANAGE_LICENSE = "manage_license"
    READ_AUDIT = "read_audit"
    MANAGE_USERS = "manage_users"
    MANAGE_JOBS = "manage_jobs"
    MANAGE_TENANTS = "manage_tenants"
    EXPORT_DATA = "export_data"


_VIEW = frozenset(
    {
        Permission.READ_RESULTS,
        Permission.READ_REPORTS,
    }
)

_OPERATOR = _VIEW | frozenset(
    {
        Permission.RUN_PIPELINE,
        Permission.WRITE_CONFIG,
        Permission.WRITE_RULES,
        Permission.PUSH_OUTPUT,
        Permission.RECONCILE,
        Permission.EXPORT_DATA,
    }
)

_ADMIN = _OPERATOR | frozenset(
    {
        Permission.MANAGE_LICENSE,
        Permission.READ_AUDIT,
        Permission.MANAGE_JOBS,
    }
)

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(Permission),
    Role.ADMIN: _ADMIN,
    Role.OPERATOR: _OPERATOR,
    # A view-only role should not be able to export data: export is the act that
    # takes a copy out of the system, which is the thing an auditor cares about.
    Role.VIEWER: _VIEW,
    Role.CLIENT: _VIEW,
}


def role_for(value: Role | str) -> Role:
    if isinstance(value, Role):
        return value
    try:
        return Role(str(value).lower())
    except ValueError as exc:
        allowed = ", ".join(role.value for role in Role)
        raise AccessDenied(f"Unknown role {value!r}. Allowed: {allowed}") from exc


@dataclass(frozen=True)
class Principal:
    """Who is acting, and over what.

    ``scope`` is the client or tenant the principal is confined to. An empty
    scope means unscoped — city-wide, for an admin — and reading a specific
    client's data is then allowed. A non-empty scope confines the read.
    """

    name: str
    role: Role = Role.VIEWER
    scope: str = ""
    authenticated: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", role_for(self.role))

    @property
    def permissions(self) -> frozenset[Permission]:
        return ROLE_PERMISSIONS[self.role]

    def can(self, permission: Permission | str) -> bool:
        return _as_permission(permission) in self.permissions

    def within_scope(self, client: str | None) -> bool:
        if not self.scope or client is None:
            return True
        return str(client) == self.scope


def _as_permission(value: Permission | str) -> Permission:
    if isinstance(value, Permission):
        return value
    try:
        return Permission(str(value))
    except ValueError as exc:
        raise AccessDenied(f"Unknown permission {value!r}") from exc


def check(
    principal: Principal,
    permission: Permission | str,
    client: str | None = None,
) -> bool:
    """True when the principal may act. Never raises for a simple no."""
    if not principal.authenticated:
        return False
    if not principal.can(permission):
        return False
    return principal.within_scope(client)


def require(
    principal: Principal,
    permission: Permission | str,
    client: str | None = None,
) -> None:
    """Raise :class:`AccessDenied` unless the principal may act.

    The message distinguishes "you cannot do this" from "you cannot do this
    here", because the two failures need different fixes: a role change versus
    a scope change.
    """
    if not principal.authenticated:
        raise AccessDenied(f"{principal.name or 'anonymous'} is not authenticated")
    wanted = _as_permission(permission)
    if wanted not in principal.permissions:
        raise AccessDenied(
            f"Role {principal.role.value!r} cannot {wanted.value!r}"
        )
    if not principal.within_scope(client):
        raise AccessDenied(
            f"{principal.name} is scoped to {principal.scope!r} and cannot act on {client!r}"
        )


@dataclass
class UserRegistry:
    """A tiny in-memory user table. Persistence is the deployment's concern."""

    users: dict[str, Principal] = field(default_factory=dict)

    def add(self, principal: Principal) -> Principal:
        self.users[principal.name] = principal
        return principal

    def get(self, name: str) -> Principal | None:
        return self.users.get(name)

    def remove(self, name: str) -> bool:
        return self.users.pop(name, None) is not None

    def names(self) -> list[str]:
        return sorted(self.users)

    def as_dicts(self) -> list[dict[str, Any]]:
        return [
            {"name": p.name, "role": p.role.value, "scope": p.scope}
            for p in (self.users[name] for name in self.names())
        ]


__all__ = [
    "ROLE_PERMISSIONS",
    "AccessDenied",
    "Permission",
    "Principal",
    "Role",
    "UserRegistry",
    "check",
    "require",
    "role_for",
]
