"""Tenant isolation and the tamper-evident audit log.

The isolation tests deliberately try to escape a tenant with ``..`` and absolute
paths — the exact moves that cause a cross-tenant data leak if a path is joined
naively. The audit tests edit and truncate a log and confirm the chain
verification catches it.
"""

from __future__ import annotations

import json

import pytest

from app_files.platform.tenancy import (
    GENESIS,
    Tenant,
    TenantError,
    canonical_slug,
    export_audit,
    get_tenant,
    list_tenants,
    read_audit,
    tenants_dir,
    verify_chain,
)


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return tmp_path


# ------------------------------------------------------------ tenant isolation
def test_tenant_creates_its_own_tree(home):
    tenant = Tenant.create("Acme Corp")
    assert tenant.id == "acme-corp"
    root = tenant.root()
    for sub in ("config", "samples", "output", "audit"):
        assert (root / sub).is_dir()
    assert list_tenants() == ["acme-corp"]


def test_tenants_are_separated_and_listed(home):
    Tenant.create("alpha")
    Tenant.create("beta")
    assert list_tenants() == ["alpha", "beta"]
    assert get_tenant("alpha").root() != get_tenant("beta").root()


def test_resolve_refuses_to_escape_a_tenant(home):
    tenant = Tenant.create("acme")
    with pytest.raises(TenantError, match="escapes"):
        tenant.resolve("..", "..", "beta", "output", "leak.csv")
    with pytest.raises(TenantError):
        tenant.resolve("/etc/passwd")


def test_a_crafted_filename_cannot_reach_another_tenant(home):
    alpha = Tenant.create("alpha")
    Tenant.create("beta")
    # A filename that tries to climb out is refused, not silently rewritten.
    with pytest.raises(TenantError):
        alpha.resolve("output", "..", "..", "beta", "samples", "secret.csv")


def test_a_normal_path_stays_inside(home):
    tenant = Tenant.create("acme")
    path = tenant.resolve("output", "clean.csv")
    assert path == tenant.root() / "output" / "clean.csv"


def test_invalid_tenant_names_are_rejected():
    with pytest.raises(TenantError):
        canonical_slug("")


# ------------------------------------------------------------------ audit log
def test_first_entry_chains_from_genesis(home):
    tenant = Tenant.create("acme")
    record = tenant.record("run.start", actor="ann", target="contacts.csv", ip="10.0.0.1")
    assert record.previous_hash == GENESIS
    entries = read_audit(tenant.audit_log_path())
    assert entries[0]["action"] == "run.start"
    assert entries[0]["actor"] == "ann"
    assert entries[0]["ip"] == "10.0.0.1"


def test_entries_form_a_valid_chain(home):
    tenant = Tenant.create("acme")
    for i in range(5):
        tenant.record("run.step", actor="ann", target=f"file-{i}.csv")
    result = verify_chain(tenant.audit_log_path())
    assert result.ok is True
    assert result.entries == 5


def test_editing_an_entry_breaks_the_chain(home):
    tenant = Tenant.create("acme")
    tenant.record("run.start", actor="ann")
    tenant.record("run.finish", actor="ann")

    path = tenant.audit_log_path()
    lines = path.read_text().splitlines()
    tampered = json.loads(lines[0])
    tampered["actor"] = "someone-else"
    lines[0] = json.dumps(tampered, sort_keys=True)
    path.write_text("\n".join(lines) + "\n")

    result = verify_chain(path)
    assert result.ok is False
    assert result.broken_at == 0
    assert "contents" in result.reason or "previous_hash" in result.reason


def test_deleting_an_entry_breaks_the_chain(home):
    tenant = Tenant.create("acme")
    for i in range(4):
        tenant.record("run.step", actor="ann", target=str(i))
    path = tenant.audit_log_path()
    lines = path.read_text().splitlines()
    del lines[1]  # remove a middle entry
    path.write_text("\n".join(lines) + "\n")
    result = verify_chain(path)
    assert result.ok is False


def test_audit_is_per_tenant(home):
    alpha = Tenant.create("alpha")
    beta = Tenant.create("beta")
    alpha.record("run.start", actor="a")
    beta.record("run.start", actor="b")
    assert len(read_audit(alpha.audit_log_path())) == 1
    assert len(read_audit(beta.audit_log_path())) == 1
    assert read_audit(alpha.audit_log_path())[0]["actor"] == "a"


def test_export_audit_includes_verification(home):
    tenant = Tenant.create("acme")
    tenant.record("run.start", actor="ann")
    document = export_audit(tenant.audit_log_path())
    assert document["verification"]["ok"] is True
    assert document["verification"]["entries"] == 1
    assert "exported_at" in document
    json.dumps(document)  # a compliance export must be serialisable


def test_state_lives_under_autoflow_home(home):
    Tenant.create("acme")
    assert tenants_dir() == home / "platform" / "tenants"
    assert str(tenants_dir()).startswith(str(home))