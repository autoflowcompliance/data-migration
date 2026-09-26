"""Layer 16 inside the real stack: tenants, the queue, and backup/restore.

Each tenant gets its own queue file, so two tenants' jobs cannot see each
other. A job running under one tenant writes only under that tenant's root, and
a backup of one tenant does not carry the other's runs.
"""

from __future__ import annotations

import pytest

from app_files.batch import run_batch
from app_files.orchestration import (
    JobQueue,
    JobSpec,
    JobState,
    Worker,
    register_handler,
)
from app_files.orchestration.workers import HANDLERS
from app_files.tenancy import (
    TenantRegistry,
    create_backup,
    restore_backup,
    verify_backup,
)


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def _clean_handlers():
    snapshot = dict(HANDLERS)
    yield
    HANDLERS.clear()
    HANDLERS.update(snapshot)


@pytest.fixture
def registry(home):
    return TenantRegistry()


def _register_batch():
    def run_batch_job(payload):
        result = run_batch(
            input_dir=payload["input_dir"],
            template=payload.get("template", "hubspot"),
            output_dir=payload["output_dir"],
            write_summary_files=False,
        )
        return {"files": len(result.items), "rows_out": result.items[0].rows_out}

    register_handler("batch", run_batch_job)


class TestTenantsRunThroughTheQueue:
    def test_each_tenant_has_its_own_queue(self, registry, tmp_path, contacts_csv):
        import shutil

        registry.create("Alpha", tenant_id="alpha")
        registry.create("Beta", tenant_id="beta")
        alpha = registry.get("alpha")
        beta = registry.get("beta")

        assert alpha.queue_file != beta.queue_file

        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        _register_batch()

        alpha_queue = JobQueue(alpha.queue_file)
        alpha_queue.submit(
            JobSpec(
                kind="batch",
                payload={"input_dir": str(input_dir), "output_dir": str(alpha.output_dir)},
            )
        )
        Worker("alpha-worker", alpha_queue).run()

        # Beta's queue never saw Alpha's job.
        assert len(JobQueue(beta.queue_file).jobs()) == 0
        assert JobQueue(alpha.queue_file).counts()["succeeded"] == 1

    def test_a_job_writes_only_inside_its_tenant(self, registry, tmp_path, contacts_csv):
        import shutil

        alpha = registry.create("Alpha", tenant_id="alpha")
        beta = registry.create("Beta", tenant_id="beta")
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        _register_batch()

        queue = JobQueue(alpha.queue_file)
        job = queue.submit(
            JobSpec(
                kind="batch",
                payload={"input_dir": str(input_dir), "output_dir": str(alpha.output_dir)},
            )
        )
        Worker("w", queue).run()
        assert queue.get(job.id).state is JobState.SUCCEEDED

        produced = [p for p in alpha.output_dir.rglob("*") if p.is_file()]
        assert produced, "the job produced no output"
        for path in produced:
            assert str(path).startswith(str(alpha.root))
        beta_files = [p for p in beta.root.rglob("*") if p.is_file()]
        assert not any(p.name == "clean_data.csv" for p in beta_files)

    def test_the_queue_state_is_part_of_what_a_backup_restores(
        self, registry, tmp_path, contacts_csv
    ):
        import shutil

        alpha = registry.create("Alpha", tenant_id="alpha")
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        _register_batch()
        queue = JobQueue(alpha.queue_file)
        queue.submit(
            JobSpec(
                kind="batch",
                payload={"input_dir": str(input_dir), "output_dir": str(alpha.output_dir)},
            )
        )
        Worker("w", queue).run()
        assert queue.counts()["succeeded"] == 1
        before = queue.counts()

        backup = create_backup(alpha, tmp_path / "backups")
        verify_backup(backup)
        alpha.delete()
        restored = registry.get("alpha", create=True)
        report = restore_backup(backup, restored)
        assert report.ok

        # The restored queue file replays to the same counts.
        assert JobQueue(restored.queue_file).counts() == before
