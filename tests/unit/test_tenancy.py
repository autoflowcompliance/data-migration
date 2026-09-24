"""Layer 16 — tenancy, backup/restore, deployment manifests."""

from __future__ import annotations

import json

import pytest
import yaml

from app_files.tenancy import (
    BackupError,
    TenantError,
    TenantRegistry,
    create_backup,
    deploy_manifest,
    deployment_plan,
    ensure_tenant,
    get_tenant,
    list_tenants,
    restore_backup,
    tenants_dir,
    verify_backup,
)


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------- tenants
class TestTenantIsolation:
    def test_tenants_dir_honours_autoflow_home(self, home):
        assert tenants_dir() == home / "tenants"

    def test_a_new_tenant_gets_its_own_folders(self, home):
        tenant = ensure_tenant("Acme Corp")
        assert tenant.id == "acme-corp"
        assert tenant.data_dir.is_dir()
        assert tenant.output_dir.is_dir()
        assert tenant.config_dir.is_dir()
        assert tenant.resolve_path("data") == tenant.data_dir

    def test_two_tenants_do_not_share_a_folder(self, home):
        alpha = ensure_tenant("Alpha", tenant_id="alpha")
        beta = ensure_tenant("Alpha", tenant_id="beta")
        assert alpha.root != beta.root
        alpha.resolve_path("output", "a.csv").write_text("alpha")
        assert not beta.resolve_path("output", "a.csv").exists()

    def test_a_tenant_cannot_escape_its_root(self, home):
        tenant = ensure_tenant("Acme")
        with pytest.raises(TenantError):
            tenant.resolve_path("..", "other-tenant", "secret.csv")
        with pytest.raises(TenantError):
            tenant.resolve_path("data", "..", "..", "escape.csv")

    def test_an_id_with_a_traversal_is_refused(self, home):
        with pytest.raises(TenantError):
            TenantRegistry().create("Evil", tenant_id="../evil")
        with pytest.raises(TenantError):
            get_tenant("../../etc")

    def test_renaming_keeps_the_folder_and_the_history(self, home):
        tenant = ensure_tenant("Old Name", tenant_id="acme")
        tenant.resolve_path("output", "run.csv").write_text("data")
        root_before = tenant.root
        tenant.rename("New Name")
        assert tenant.root == root_before
        assert tenant.resolve_path("output", "run.csv").read_text() == "data"
        assert get_tenant("acme").name == "New Name"

    def test_ensure_tenant_is_idempotent(self, home):
        first = ensure_tenant("Acme", tenant_id="acme")
        second = ensure_tenant("Acme", tenant_id="acme")
        assert first.root == second.root
        assert len(list_tenants()) == 1

    def test_duplicate_id_is_refused(self, home):
        TenantRegistry().create("One", tenant_id="acme")
        with pytest.raises(TenantError):
            TenantRegistry().create("Two", tenant_id="acme")

    def test_missing_tenant_raises_unless_create_requested(self, home):
        with pytest.raises(TenantError):
            get_tenant("nobody")
        assert get_tenant("nobody", create=True).root.is_dir()

    def test_usage_counts_only_this_tenants_files(self, home):
        alpha = ensure_tenant("Alpha", tenant_id="alpha")
        beta = ensure_tenant("Beta", tenant_id="beta")
        alpha.resolve_path("data", "a.csv").write_text("x" * 100)
        alpha.resolve_path("output", "b.csv").write_text("y" * 50)
        beta.resolve_path("data", "c.csv").write_text("z" * 999)
        usage = alpha.usage()
        # The tenant's own metadata counts too, so assert the data subtrees.
        assert usage["breakdown"]["data"]["bytes"] == 100
        assert usage["breakdown"]["output"]["bytes"] == 50
        assert usage["tenant"] == "alpha"


# ----------------------------------------------------------------------- backup
class TestBackupAndRestore:
    def _populate(self, tenant):
        tenant.resolve_path("data", "input.csv").write_text("a,b\n1,2\n")
        tenant.resolve_path("output", "clean.csv").write_text("a,b\n1,2\n")
        tenant.resolve_path("config", "config.yaml").write_text("fields: []\n")

    def test_a_backup_lists_every_file_with_a_digest(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")
        assert backup.path.exists()
        assert backup.manifest.file_count == 4  # 3 files + tenant.json

    def test_verification_passes_on_an_intact_backup(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")
        manifest = verify_backup(backup)
        assert manifest.file_count == backup.manifest.file_count

    def test_verification_fails_on_a_tampered_archive(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")

        # Rewrite the archive with one file's contents changed.
        staging = home / "tamper"
        staging.mkdir()
        import tarfile

        with tarfile.open(backup.path, "r:gz") as tar:
            tar.extractall(staging, filter="data")
        (staging / "data" / "input.csv").write_text("TAMPERED\n")
        with tarfile.open(backup.path, "w:gz") as tar:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    tar.add(path, arcname=str(path.relative_to(staging)))

        with pytest.raises(BackupError, match="mismatch"):
            verify_backup(backup)

    def test_restore_reproduces_the_original_tree(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")
        original = tenant.tree()

        tenant.delete()
        restored = ensure_tenant("Acme", tenant_id="acme")
        report = restore_backup(backup, restored)

        assert report.ok
        assert report.missing == []
        assert report.mismatched == []
        assert restored.tree() == original
        assert restored.resolve_path("data", "input.csv").read_text() == "a,b\n1,2\n"

    def test_restore_refuses_a_corrupt_archive_before_writing(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")

        # Corrupt the manifest digest for one file.
        manifest_path = backup.path.with_suffix(backup.path.suffix + ".manifest.json")
        data = json.loads(manifest_path.read_text())
        data["files"]["data/input.csv"] = "0" * 64
        manifest_path.write_text(json.dumps(data))

        target = ensure_tenant("Restored", tenant_id="restored")
        with pytest.raises(BackupError):
            restore_backup(backup, target)
        # Nothing was written, because verification runs first.
        assert not target.resolve_path("data", "input.csv").exists()

    def test_restore_reports_a_missing_file_rather_than_claiming_success(self, home):
        tenant = ensure_tenant("Acme", tenant_id="acme")
        self._populate(tenant)
        backup = create_backup(tenant, home / "backups")

        # Delete a file inside the archive but keep the manifest entry.
        import tarfile

        staging = home / "strip"
        staging.mkdir()
        with tarfile.open(backup.path, "r:gz") as tar:
            tar.extractall(staging, filter="data")
        (staging / "output" / "clean.csv").unlink()
        with tarfile.open(backup.path, "w:gz") as tar:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    tar.add(path, arcname=str(path.relative_to(staging)))

        target = ensure_tenant("Restored", tenant_id="restored")
        report = restore_backup(backup, target, verify=False)
        assert not report.ok
        assert "output/clean.csv" in report.missing


# -------------------------------------------------------------------- deployment
class TestDeploymentManifests:
    def test_docker_compose_is_valid_yaml(self):
        plan = deployment_plan("docker")
        compose = yaml.safe_load(plan.files["docker-compose.yml"])
        assert compose["services"]["dataflow"]["image"] == "dataflow:latest"

    def test_compose_binds_port_with_a_fallback(self):
        compose = yaml.safe_load(deployment_plan("docker").files["docker-compose.yml"])
        assert compose["services"]["dataflow"]["ports"] == ["${PORT:-8080}:${PORT:-8080}"]

    def test_render_blueprint_does_not_set_port(self):
        plan = deployment_plan("render")
        text = plan.files["render.yaml"]
        assert "PORT" not in yaml.dump(yaml.safe_load(text))
        blueprint = yaml.safe_load(text)
        assert blueprint["services"][0]["healthCheckPath"] == "/health"

    def test_kubernetes_manifest_is_two_valid_documents(self):
        docs = list(yaml.safe_load_all(deployment_plan("kubernetes").files["dataflow.yaml"]))
        assert [d["kind"] for d in docs] == ["Deployment", "Service"]
        container = docs[0]["spec"]["template"]["spec"]["containers"][0]
        probes = {p["httpGet"]["path"] for p in (container["readinessProbe"], container["livenessProbe"])}
        assert probes == {"/ready", "/health"}

    def test_every_target_sets_both_state_homes(self):
        for target in ("docker", "render", "kubernetes"):
            plan = deployment_plan(target)
            for content in plan.files.values():
                if content.strip().startswith("{"):
                    assert "AUTOFLOW_HOME" in content
                    continue
                parsed = list(yaml.safe_load_all(content))
                blob = json.dumps(parsed, default=str)
                assert "AUTOFLOW_HOME" in blob
                assert "DATAREADY_HOME" in blob

    def test_an_unknown_target_is_refused(self):
        with pytest.raises(ValueError, match="Unknown deploy target"):
            deployment_plan("heroku")

    def test_a_custom_port_reaches_the_manifests(self):
        compose = yaml.safe_load(deployment_plan("docker", port=9000).files["docker-compose.yml"])
        assert "9000" in compose["services"]["dataflow"]["ports"][0]
        docs = list(yaml.safe_load_all(deployment_plan("kubernetes", port=9000).files["dataflow.yaml"]))
        assert docs[0]["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"] == 9000

    def test_deploy_manifest_writes_the_files(self, tmp_path):
        written = deploy_manifest("render", tmp_path)
        assert {p.name for p in written} == {"render.yaml", "render.json"}
        assert all(p.exists() for p in written)
        assert (tmp_path / "render.yaml").exists()

    def test_extra_env_reaches_every_target(self):
        env = {"DATAREADY_PURCHASE_URL": "https://example.test/buy"}
        compose = yaml.safe_load(
            deployment_plan("docker", env=env).files["docker-compose.yml"]
        )
        assert compose["services"]["dataflow"]["environment"]["DATAREADY_PURCHASE_URL"] == env[
            "DATAREADY_PURCHASE_URL"
        ]


# ----------------------------------------------------------------- real-file proof
class TestTenantRoundTripOnRealFiles:
    def test_two_tenants_run_the_same_real_file_without_crossing(self, home, samples_dir):
        """End to end: real CSV in, isolated outputs out, backup and restore."""
        from app_files.ingestion import read_any
        from app_files.output import write_any
        from app_files.pipeline import run_pipeline

        source = samples_dir / "messy_contacts.csv"
        alpha = ensure_tenant("Alpha", tenant_id="alpha")
        beta = ensure_tenant("Beta", tenant_id="beta")

        results = {}
        for tenant in (alpha, beta):
            frame = read_any(source, filename=source.name)
            result = run_pipeline(frame, crm="hubspot", source_filename=source.name)
            target = tenant.resolve_path("output", f"{tenant.id}_clean")
            written = write_any(result.clean_frame, target, "csv")
            results[tenant.id] = (result, written)

        assert results["alpha"][0].summary()["rows_out"] == results["beta"][0].summary()["rows_out"]
        assert results["alpha"][0].summary()["rows_out"] > 0
        for tenant in (alpha, beta):
            written = results[tenant.id][1]
            assert str(written).startswith(str(tenant.root))
            # The other tenant's folder must not contain this file.
            other = beta if tenant is alpha else alpha
            assert not str(written).startswith(str(other.root))

        backup = create_backup(alpha, home / "backups")
        verify_backup(backup)
        before = (alpha.output_dir / "alpha_clean.csv").read_text()
        alpha.delete()
        restored = ensure_tenant("Alpha", tenant_id="alpha")
        report = restore_backup(backup, restored)
        assert report.ok
        assert (restored.output_dir / "alpha_clean.csv").read_text() == before
        # Beta was never touched by Alpha's backup or restore.
        assert (beta.output_dir / "beta_clean.csv").exists()
