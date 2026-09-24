"""The ``dedupe:`` block must bind in the real CLI and batch entry points."""

from __future__ import annotations

import shutil

import pandas as pd
import pytest

from app_files.cli import main

CONTACTS = (
    "First Name,Last Name\n"
    "John,Smith\n"
    "Jon,Smith\n"
    "Jane,Doe\n"
    "Janet,Doe\n"
)

CONFIG = """crm: Contacts
version: "1.0"
fields:
  - name: first_name
    aliases: ["First Name"]
  - name: last_name
    aliases: ["Last Name"]
dedupe:
  rules:
    - columns: [first_name, last_name]
      threshold: 0.85
      metric: jaro_winkler
"""


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def case(tmp_path):
    config = tmp_path / "crm.yaml"
    config.write_text(CONFIG, encoding="utf-8")
    source = tmp_path / "contacts.csv"
    source.write_text(CONTACTS, encoding="utf-8")
    return config, source


class TestSingleFileCli:
    def test_the_deduped_copy_is_written(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        assert (out / "deduped_data.csv").is_file()

    def test_the_pipeline_output_keeps_every_row(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        clean = pd.read_csv(out / "clean_data.csv")
        assert len(clean) == 4

    def test_near_duplicates_are_folded_out(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        deduped = pd.read_csv(out / "deduped_data.csv")
        assert len(deduped) == 2
        assert deduped["first_name"].tolist() == ["John", "Jane"]

    def test_the_merge_log_is_written(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        merges = pd.read_csv(out / "duplicates_removed.csv")
        assert len(merges) == 2
        assert set(merges["reason"]) == {"fuzzy match"}

    def test_the_line_is_printed(self, home, case, tmp_path, capsys):
        config, source = case
        main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        out = capsys.readouterr().out
        assert "Dedupe:" in out
        assert "2 near-duplicate row(s) removed from 4" in out

    def test_a_block_less_config_writes_nothing_extra(self, home, tmp_path):
        source = tmp_path / "contacts.csv"
        source.write_text(CONTACTS, encoding="utf-8")
        out = tmp_path / "out"
        main(["-i", str(source), "-c", "hubspot", "-o", str(out)])
        assert not (out / "deduped_data.csv").exists()
        assert not (out / "duplicates_removed.csv").exists()

    def test_a_malformed_block_fails_the_run_cleanly(self, home, tmp_path, capsys):
        config = tmp_path / "bad.yaml"
        config.write_text(
            "crm: X\nfields: []\ndedupe:\n  rules:\n    - {threshold: 0.9}\n",
            encoding="utf-8",
        )
        source = tmp_path / "contacts.csv"
        source.write_text(CONTACTS, encoding="utf-8")
        code = main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        assert code == 2
        assert "Invalid dedupe configuration" in capsys.readouterr().err


class TestBatchCli:
    @pytest.fixture
    def inbox(self, case, tmp_path):
        _, source = case
        folder = tmp_path / "inbox"
        folder.mkdir()
        shutil.copy(source, folder / "a.csv")
        return folder

    def test_each_file_gets_a_deduped_copy(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        assert (out / "a" / "deduped_data.csv").is_file()

    def test_the_summary_counts_the_work(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        summary = pd.read_csv(out / "summary.csv")
        assert "duplicates_removed" in summary.columns
        assert summary["duplicates_removed"].tolist() == [2]

    def test_a_block_less_template_writes_nothing_extra(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)])
        assert not (out / "a" / "deduped_data.csv").exists()
        summary = pd.read_csv(out / "summary.csv")
        assert summary["duplicates_removed"].tolist() == [0]
