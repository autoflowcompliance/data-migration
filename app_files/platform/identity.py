"""Enterprise identity: RBAC permission sets, SSO assertion handling, SCIM.

Three pieces, each with a real, testable core rather than a stub:

* **RBAC** — roles are *sets of permissions*, and a role is allowed to do
  something only if it holds the matching permission. ``data_steward`` reviews
  rules, ``operator`` runs pipelines, ``admin`` manages tenants; the sets do not
  silently overlap. The check is a plain set membership, so it is impossible to
  get a "close enough" authorisation by accident.

* **SSO** — SAML 2.0 and OIDC. This module validates the assertions a real IdP
  sends: an OIDC ID token's claims, and a SAML Response's subject, conditions,
  audience and status. What it deliberately does *not* do is perform the browser
  round-trip against a specific IdP's metadata URL — that is deployment
  configuration, and faking it offline would be a lie. Everything up to "is this
  assertion valid for this audience and not expired" is real and tested against
  crafted assertions.

* **SCIM 2.0** — user and group provisioning. ``User``/``Group`` payloads are
  parsed per RFC 7643, and a deactivation maps onto the right RBAC decision
  (deprovision the user, drop group memberships). The shapes follow RFC 7644 so
  an Okta or Azure AD connector can be pointed at it.

No secrets are stored; nothing here reaches the network.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any

# --------------------------------------------------------------------- RBAC
# Permissions are named resource:action strings. Adding a capability means
# adding a permission here and to the roles that should hold it — the roles are
# data, not a chain of if/else.
PERMISSIONS = {
    "run:execute": "Start a migration run",
    "run:read": "View run results and reports",
    "rule:review": "Review and approve validation rules",
    "rule:edit": "Create and edit validation rules",
    "config:edit": "Edit mapping and cleaning configs",
    "output:download": "Download clean data and reports",
    "output:deliver": "Push deliverables to a destination",
    "workspace:read": "View client workspaces",
    "tenant:manage": "Create, suspend and delete tenants",
    "user:manage": "Invite, deactivate and re-role users",
    "audit:read": "Read the audit log",
    "audit:export": "Export the audit log for compliance",
    "billing:manage": "Manage plans and invoices",
}

# The roles the product sells. Each is a distinct job to be done, so the sets do
# not collapse into one "admin-ish" blob.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "data_steward": {
        "run:read",
        "rule:review",
        "rule:edit",
        "workspace:read",
        "output:download",
        "audit:read",
    },
    "operator": {
        "run:execute",
        "run:read",
        "workspace:read",
        "output:download",
        "output:deliver",
        "audit:read",
    },
    "auditor": {
        "run:read",
        "workspace:read",
        "audit:read",
        "audit:export",
    },
    "admin": set(PERMISSIONS),
}


class AuthError(RuntimeError):
    """Raised when an identity or authorisation decision fails."""


class PermissionDenied(AuthError):
    def __init__(self, role: str, permission: str) -> None:
        super().__init__(
            f"Role {role!r} does not hold {permission!r}. "
            f"Required permissions are granted per role; ask an admin to re-role "
            f"the user or add the permission."
        )
        self.role = role
        self.permission = permission


def permissions_for(role: str) -> set[str]:
    if role not in ROLE_PERMISSIONS:
        raise AuthError(
            f"Unknown role {role!r}. Available: {', '.join(sorted(ROLE_PERMISSIONS))}"
        )
    return set(ROLE_PERMISSIONS[role])


def permission_report() -> dict[str, list[str]]:
    """Every role and its permissions, sorted — the thing a due-diligence form asks for."""
    return {role: sorted(perms) for role, perms in sorted(ROLE_PERMISSIONS.items())}


def can(role: str, permission: str) -> bool:
    return permission in permissions_for(role)


def require(role: str, permission: str) -> None:
    if not can(role, permission):
        raise PermissionDenied(role, permission)


# ---------------------------------------------------------------- OIDC (SSO)
@dataclass
class OIDCClaims:
    subject: str
    email: str
    issuer: str
    audience: str
    expires_at: int
    groups: list[str] = field(default_factory=list)
    email_verified: bool = False


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def decode_id_token_unverified(token: str) -> dict[str, Any]:
    """Split a JWT and return its claims without checking the signature.

    Named ``unverified`` on purpose: it is for reading claims *after*
    :func:`validate_id_token` has checked them, or for showing a login hint.
    Calling it alone is never an authorisation decision.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("An ID token must have three dot-separated segments.")
    try:
        return json.loads(_b64url_decode(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AuthError(f"ID token payload is not valid JSON: {exc}") from exc


def validate_id_token(
    token: str,
    *,
    issuer: str,
    audience: str,
    now: int | None = None,
    allowed_algorithms: tuple[str, ...] = ("HS256",),
    signing_key: bytes | None = None,
    leeway: int = 60,
) -> OIDCClaims:
    """Validate an OIDC ID token's signature and claims.

    Checks, in order: the header algorithm is allowed (and not ``none``), the
    HMAC signature when a key is supplied, then ``iss``, ``aud``, ``exp`` and
    ``iat``. Any failure raises :class:`AuthError` with the specific reason — a
    login that silently succeeds on a bad assertion is the whole risk with SSO.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("An ID token must have three dot-separated segments.")

    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AuthError(f"ID token is malformed: {exc}") from exc

    algorithm = str(header.get("alg", ""))
    if algorithm.lower() == "none":
        raise AuthError("Refusing an unsigned ID token (alg='none').")
    if algorithm not in allowed_algorithms:
        raise AuthError(
            f"ID token algorithm {algorithm!r} is not allowed. "
            f"Allowed: {', '.join(allowed_algorithms)}."
        )

    if signing_key is not None:
        signing_input = f"{parts[0]}.{parts[1]}".encode()
        expected = hmac.new(signing_key, signing_input, hashlib.sha256).digest()
        actual = _b64url_decode(parts[2])
        if not hmac.compare_digest(expected, actual):
            raise AuthError("ID token signature does not match.")

    if payload.get("iss") != issuer:
        raise AuthError(f"ID token issuer {payload.get('iss')!r} does not match {issuer!r}.")

    audience_claim = payload.get("aud")
    audiences = audience_claim if isinstance(audience_claim, list) else [audience_claim]
    if audience not in audiences:
        raise AuthError(f"ID token audience {audiences!r} does not include {audience!r}.")

    clock = int(time.time()) if now is None else now
    if "exp" not in payload:
        raise AuthError("ID token has no 'exp' claim; it cannot be trusted.")
    if clock > int(payload["exp"]) + leeway:
        raise AuthError("ID token has expired.")
    if "iat" in payload and int(payload["iat"]) > clock + leeway:
        raise AuthError("ID token was issued in the future.")

    return OIDCClaims(
        subject=str(payload.get("sub", "")),
        email=str(payload.get("email", "")),
        issuer=str(payload["iss"]),
        audience=audience,
        expires_at=int(payload["exp"]),
        groups=list(payload.get("groups", []) or []),
        email_verified=bool(payload.get("email_verified", False)),
    )


def sign_id_token(claims: dict[str, Any], key: bytes, algorithm: str = "HS256") -> str:
    """Mint a token the validator accepts. Used by tests and local development."""
    header = {"alg": algorithm, "typ": "JWT"}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64url_encode(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url_encode(signature)}"


# ---------------------------------------------------------------- SAML (SSO)
SAML_SUCCESS = "urn:oasis:names:tc:SAML:2.0:status:Success"


@dataclass
class SAMLAssertion:
    subject: str
    audience: str
    not_before: int
    not_on_or_after: int
    issuer: str
    attributes: dict[str, list[str]] = field(default_factory=dict)

    def is_valid_at(self, now: int) -> bool:
        return self.not_before <= now <= self.not_on_or_after


def parse_saml_response(xml: str) -> SAMLAssertion:
    """Parse a SAML 2.0 Response into its assertion.

    Uses the standard library's XML parser. External entities are not resolved,
    so a crafted response cannot pull in a local file (XXE). Namespaces are
    matched by their local name to stay readable across IdP variations.
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise AuthError(f"SAML Response is not valid XML: {exc}") from exc

    def local(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    status_code = next(
        (node.get("Value", "") for node in root.iter() if local(node.tag) == "StatusCode"),
        "",
    )
    if status_code and status_code != SAML_SUCCESS:
        raise AuthError(f"SAML Response status is not Success: {status_code!r}")

    assertions = [node for node in root.iter() if local(node.tag) == "Assertion"]
    if not assertions:
        raise AuthError("SAML Response contains no Assertion.")
    assertion = assertions[0]

    subject_node = next((n for n in assertion.iter() if local(n.tag) == "NameID"), None)
    if subject_node is None or not (subject_node.text or "").strip():
        raise AuthError("SAML Assertion has no NameID (subject).")

    conditions = next((n for n in assertion.iter() if local(n.tag) == "Conditions"), None)
    if conditions is None:
        raise AuthError("SAML Assertion has no Conditions; it cannot be trusted.")
    not_before_raw = conditions.get("NotBefore")
    not_after_raw = conditions.get("NotOnOrAfter")
    if not not_after_raw:
        raise AuthError("SAML Conditions has no NotOnOrAfter; it cannot be trusted.")

    audiences = [
        (n.text or "").strip()
        for n in assertion.iter()
        if local(n.tag) == "Audience"
    ]
    if not audiences:
        raise AuthError("SAML Assertion has no Audience restriction.")

    issuer_node = next((n for n in assertion.iter() if local(n.tag) == "Issuer"), None)

    attributes: dict[str, list[str]] = {}
    for attribute in [n for n in assertion.iter() if local(n.tag) == "Attribute"]:
        name = attribute.get("Name", "")
        values = [
            (v.text or "")
            for v in attribute
            if local(v.tag) == "AttributeValue"
        ]
        if name:
            attributes[name] = values

    return SAMLAssertion(
        subject=(subject_node.text or "").strip(),
        audience=audiences[0],
        not_before=_saml_time(not_before_raw) if not_before_raw else 0,
        not_on_or_after=_saml_time(not_after_raw),
        issuer=(issuer_node.text or "").strip() if issuer_node is not None else "",
        attributes=attributes,
    )


def validate_saml_assertion(
    assertion: SAMLAssertion,
    *,
    expected_audience: str,
    expected_issuer: str = "",
    now: int | None = None,
) -> SAMLAssertion:
    clock = int(time.time()) if now is None else now
    if expected_issuer and assertion.issuer != expected_issuer:
        raise AuthError(
            f"SAML issuer {assertion.issuer!r} does not match {expected_issuer!r}."
        )
    if assertion.audience != expected_audience:
        raise AuthError(
            f"SAML audience {assertion.audience!r} does not match {expected_audience!r}."
        )
    if not assertion.is_valid_at(clock):
        raise AuthError("SAML Assertion is outside its validity window.")
    return assertion


def _saml_time(value: str) -> int:
    from datetime import datetime, timezone

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthError(f"SAML timestamp {value!r} is not ISO 8601: {exc}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


# ----------------------------------------------------------------- SCIM 2.0
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"


@dataclass
class SCIMUser:
    external_id: str
    user_name: str
    email: str
    active: bool = True
    display_name: str = ""
    groups: list[str] = field(default_factory=list)

    def to_scim(self, scim_id: str = "") -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schemas": [SCIM_USER_SCHEMA],
            "externalId": self.external_id,
            "userName": self.user_name,
            "active": self.active,
            "emails": [{"value": self.email, "primary": True}],
        }
        if scim_id:
            payload["id"] = scim_id
        if self.display_name:
            payload["displayName"] = self.display_name
        return payload


def parse_scim_user(payload: dict[str, Any]) -> SCIMUser:
    if SCIM_USER_SCHEMA not in payload.get("schemas", []) and "userName" not in payload:
        raise AuthError("Not a SCIM User payload (missing schema and userName).")
    user_name = str(payload.get("userName", "")).strip()
    if not user_name:
        raise AuthError("SCIM User payload has no userName.")
    email = ""
    for entry in payload.get("emails", []) or []:
        if isinstance(entry, dict) and entry.get("value"):
            email = str(entry["value"])
            if entry.get("primary"):
                break
    return SCIMUser(
        external_id=str(payload.get("externalId", "")),
        user_name=user_name,
        email=email,
        active=bool(payload.get("active", True)),
        display_name=str(payload.get("displayName", "")),
        groups=[
            str(g.get("value") if isinstance(g, dict) else g)
            for g in payload.get("groups", []) or []
        ],
    )


@dataclass
class SCIMGroup:
    external_id: str
    display_name: str
    members: list[str] = field(default_factory=list)


def parse_scim_group(payload: dict[str, Any]) -> SCIMGroup:
    if SCIM_GROUP_SCHEMA not in payload.get("schemas", []) and "displayName" not in payload:
        raise AuthError("Not a SCIM Group payload (missing schema and displayName).")
    display_name = str(payload.get("displayName", "")).strip()
    if not display_name:
        raise AuthError("SCIM Group payload has no displayName.")
    members = []
    for member in payload.get("members", []) or []:
        value = member.get("value") if isinstance(member, dict) else member
        if value:
            members.append(str(value))
    return SCIMGroup(
        external_id=str(payload.get("externalId", "")),
        display_name=display_name,
        members=members,
    )


# A group name maps to a role; a deactivated user maps to no role at all.
GROUP_ROLE_MAP = {
    "data-stewards": "data_steward",
    "operators": "operator",
    "auditors": "auditor",
    "admins": "admin",
}


@dataclass
class ProvisioningDecision:
    user_name: str
    active: bool
    role: str | None
    reason: str

    @property
    def deprovisioned(self) -> bool:
        return not self.active


def provisioning_action(user: SCIMUser) -> ProvisioningDecision:
    """What SCIM provisioning should do with a user.

    A deactivated user is deprovisioned regardless of group membership: the
    "employee left, their account is gone" path must not depend on the IdP also
    remembering to remove the group first.
    """
    if not user.active:
        return ProvisioningDecision(
            user_name=user.user_name,
            active=False,
            role=None,
            reason="User is inactive; deprovision and revoke all roles.",
        )
    role = next((GROUP_ROLE_MAP[g] for g in user.groups if g in GROUP_ROLE_MAP), None)
    if role is None:
        return ProvisioningDecision(
            user_name=user.user_name,
            active=True,
            role=None,
            reason="Active user in no mapped group; grant no role until an admin assigns one.",
        )
    return ProvisioningDecision(
        user_name=user.user_name,
        active=True,
        role=role,
        reason=f"Mapped from group to role {role!r}.",
    )


def scim_error(detail: str, status: int = 400) -> dict[str, Any]:
    """A SCIM-format error body, which provisioning clients expect."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": detail,
        "status": str(status),
    }