"""The ``privacy:`` block must bind in the real CLI and batch entry points.

Drives ``app_files.cli.main`` unchanged and asserts on the artifacts it writes.
The gap this closes was not in the privacy layer (which had tests) but in the
fact that no unattended caller read the config's ``privacy:`` block.
"""

from __future__ import annotations

import hashlib
import shutil

import pandas as pd
import pytest

from app_files.cli import main

CONTACTS = (
    "First Name,Last Name,Email Address,Phone 1,Notes\n"
    "Ann,Smith,ann.smith@example.com,(617) 498-3000,Call ann.smith@example.com\n"
    "Bob,Jones,bob@example.com,512.876.5432,\n"
)

CONFIG = """crm: Contacts
version: "1.0"
fields:
  - name: firstname
    aliases: ["First Name"]
  - name: lastname
    aliases: ["Last Name"]
  - name: email
    aliases: ["Email Address"]
  - name: phone
    aliases: ["Phone 1"]
  - name: notes
    aliases: ["Notes"]
privacy:
  default_strategy: redact
  fields:
    - column: email
      strategy: hash
    - column: phone
      strategy: partial
"""


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def case(tmp_path):
    """A config declaring privacy and a file carrying five known PII values."""
    config = tmp_path / "crm.yaml"
    config.write_text(CONFIG, encoding="utf-8")
    source = tmp_path / "contacts.csv"
    source.write_text(CONTACTS, encoding="utf-8")
    return config, source


class TestSingleFileCli:
    def test_the_masked_copy_is_written(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        assert (out / "masked_data.csv").is_file()

    def test_the_original_output_is_not_masked(self, home, case, tmp_path):
        """Masking is additive: the frozen pipeline's own file keeps the raw
        values so a run that never asked for privacy is unaffected."""
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        clean = pd.read_csv(out / "clean_data.csv")
        assert clean.loc[0, "email"] == "ann.smith@example.com"
        assert str(clean.loc[0, "phone"]).endswith("3000")

    def test_every_known_pii_value_is_masked(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        masked = pd.read_csv(out / "masked_data.csv")
        text = masked.to_csv(index=False)
        for raw in ("ann.smith@example.com", "bob@example.com", "(617) 498-3000"):
            assert raw not in text
        # The email hash is deterministic and the phone keeps its last four.
        expected = hashlib.sha256(b"ann.smith@example.com").hexdigest()
        assert masked.loc[0, "email"] == expected
        assert masked.loc[0, "phone"].endswith("3000")

    def test_the_free_text_column_is_redacted_too(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        masked = pd.read_csv(out / "masked_data.csv")
        assert "[REDACTED]" in masked.loc[0, "notes"]

    def test_the_report_gains_the_privacy_card(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        html = (out / "qa_report.html").read_text(encoding="utf-8")
        assert "privacy" in html.lower()
        assert (out / "privacy_report.html").is_file()

    def test_a_privacy_less_config_writes_nothing_extra(self, home, tmp_path):
        """The regression guard: no ``privacy:`` block means byte-identical
        behaviour, so the frozen pipeline is untouched by this feature."""
        source = tmp_path / "contacts.csv"
        source.write_text(CONTACTS, encoding="utf-8")
        out = tmp_path / "out"
        main(["-i", str(source), "-c", "hubspot", "-o", str(out)])
        assert not (out / "masked_data.csv").exists()
        assert not (out / "privacy_report.html").exists()

    def test_a_malformed_block_fails_the_run_cleanly(self, home, tmp_path, capsys):
        """A privacy typo must stop the run, not silently pass PII through."""
        config = tmp_path / "bad.yaml"
        config.write_text(
            "crm: X\nfields:\n  - name: email\n    aliases: [\"Email Address\"]\n"
            "privacy:\n  default_strategy: nope\n",
            encoding="utf-8",
        )
        source = tmp_path / "contacts.csv"
        source.write_text(CONTACTS, encoding="utf-8")
        code = main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        assert code == 2
        assert "Invalid privacy configuration" in capsys.readouterr().err

    def test_the_line_is_printed(self, home, case, tmp_path, capsys):
        config, source = case
        main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        out = capsys.readouterr().out
        assert "Privacy:" in out
        assert "5 value(s) detected, 5 masked" in out


class TestBatchCli:
    @pytest.fixture
    def inbox(self, case, tmp_path):
        _, source = case
        folder = tmp_path / "inbox"
        folder.mkdir()
        shutil.copy(source, folder / "a.csv")
        shutil.copy(source, folder / "b.csv")
        return folder

    def test_each_file_gets_a_masked_copy(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        assert (out / "a" / "masked_data.csv").is_file()
        assert (out / "b" / "masked_data.csv").is_file()

    def test_the_summary_counts_masked_values(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        summary = pd.read_csv(out / "summary.csv")
        assert "privacy_masked" in summary.columns
        assert summary["privacy_masked"].tolist() == [5, 5]

    def test_a_privacy_less_template_writes_nothing_extra(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main(
            ["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)]
        )
        assert not (out / "a" / "masked_data.csv").exists()
        summary = pd.read_csv(out / "summary.csv")
        assert summary["privacy_masked"].tolist() == [0, 0]
