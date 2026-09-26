"""The shared binding sequence every run path uses.

The flat CLI and the batch engine each open-coded the same order — rules,
privacy, normalization, dedupe — and ``migrate`` open-coded none of them. That
divergence is what let a committed migration write raw PII for a config that
declared masking. These tests pin the one helper that replaced it.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.config_bindings import (
    apply_configured_bindings,
    write_bound_deliverables,
)
from app_files.pipeline import run_pipeline

SOURCE = (
    "Email Address,First Name,Last Name,Phone,Amount\n"
    "john@acme.com,John,Smith,+14155550100,10\n"
    "jon@acme.com,Jon,Smith,+14155550101,20\n"
)

ALL_ON = """
crm: All On
version: "1.0"
fields:
  - name: email
    required: true
    aliases: ["Email Address"]
  - name: firstname
    aliases: ["First Name"]
  - name: lastname
    aliases: ["Last Name"]
  - name: phone
    aliases: ["Phone"]
rules:
  - name: email_shape
    field: email
    type: regex
    pattern: "^[^@\\\\s]+@[^@\\\\s]+\\\\.[^@\\\\s]+$"
    severity: warning
privacy:
  default_strategy: redact
  fields:
    - column: email
      strategy: hash
dedupe:
  rules:
    - columns: [firstname, lastname]
      threshold: 0.85
      metric: jaro_winkler
"""

BARE = """
crm: Bare
version: "1.0"
fields:
  - name: email
    aliases: ["Email Address"]
  - name: firstname
    aliases: ["First Name"]
  - name: lastname
    aliases: ["Last Name"]
  - name: phone
    aliases: ["Phone"]
"""


@pytest.fixture(autouse=True)
def state_home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path / "state"


def _frame() -> pd.DataFrame:
    import io

    return pd.read_csv(io.StringIO(SOURCE), dtype=str, keep_default_na=False)


def _config(tmp_path, text: str, name: str = "crm.yaml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


class TestApplyBindings:
    def test_a_config_without_blocks_resolves_them_all_to_none(self, tmp_path):
        result = run_pipeline(_frame(), crm=str(_config(tmp_path, BARE)))
        bindings = apply_configured_bindings(result, str(tmp_path / "crm.yaml"))
        assert bindings.privacy is None
        assert bindings.normalization is None
        assert bindings.dedupe is None
        assert bindings.declared_rules == 0

    def test_declared_blocks_are_each_resolved(self, tmp_path):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        bindings = apply_configured_bindings(result, str(config))
        assert bindings.declared_rules == 1
        assert bindings.privacy is not None
        assert bindings.dedupe is not None

    def test_privacy_masks_the_copy_not_the_pipeline_frame(self, tmp_path):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        bindings = apply_configured_bindings(result, str(config))
        # The pipeline's own frame keeps the address; only the masked copy hides it.
        assert result.clean_frame["email"].str.contains("@").any()
        assert not bindings.privacy.masked_frame["email"].str.contains("@").any()

    def test_the_pii_card_lands_in_the_reported_html(self, tmp_path):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        bindings = apply_configured_bindings(result, str(config))
        assert "PII" in bindings.qa_report_html or "privacy" in bindings.qa_report_html.lower()


class TestWriteBoundDeliverables:
    def test_a_bare_config_writes_nothing(self, tmp_path):
        config = _config(tmp_path, BARE)
        result = run_pipeline(_frame(), crm=str(config))
        bindings = apply_configured_bindings(result, str(config))
        out = tmp_path / "out"
        assert write_bound_deliverables(bindings, out) == {}
        assert not out.exists() or list(out.iterdir()) == []

    def test_declared_blocks_write_their_artifacts(self, tmp_path):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        bindings = apply_configured_bindings(result, str(config))
        out = tmp_path / "out"
        written = write_bound_deliverables(bindings, out)
        assert (out / "masked_data.csv").is_file()
        assert (out / "deduped_data.csv").is_file()
        assert "qa_report" in written

    def test_persist_rules_false_leaves_no_accepted_ruleset(self, tmp_path, state_home):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        apply_configured_bindings(result, str(config), persist_rules=False)
        assert not (state_home / "rules").exists()

    def test_persist_rules_true_records_the_accepted_ruleset(self, tmp_path, state_home):
        config = _config(tmp_path, ALL_ON)
        result = run_pipeline(_frame(), crm=str(config))
        apply_configured_bindings(result, str(config))
        assert (state_home / "rules").exists()
