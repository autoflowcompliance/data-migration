"""The ``normalization:`` block must bind in the real CLI and batch entry points.

The gap this closes was not in the engine (which had tests) but in the fact
that no unattended caller read a config's ``normalization:`` block, so the
module had zero callers outside itself.
"""

from __future__ import annotations

import shutil

import pandas as pd
import pytest

from app_files.cli import main

ORDERS = (
    "Company,Address,Amount\n"
    'Acme,"123 north maple ave., springfield, il 62704","€1,000.00"\n'
    'Beta,"456 S Oak St, Springfield, IL 62704","£500.00"\n'
)

CONFIG = """crm: Orders
version: "1.0"
fields:
  - name: company
    aliases: ["Company"]
  - name: address
    aliases: ["Address"]
  - name: amount
    aliases: ["Amount"]
normalization:
  addresses:
    - column: address
  currency:
    target: USD
    columns: [amount]
    rates:
      - {base: EUR, quote: USD, rate: 1.08, as_of: 2026-01-15}
      - {base: GBP, quote: USD, rate: 1.27, as_of: 2026-01-15}
"""


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def case(tmp_path):
    config = tmp_path / "crm.yaml"
    config.write_text(CONFIG, encoding="utf-8")
    source = tmp_path / "orders.csv"
    source.write_text(ORDERS, encoding="utf-8")
    return config, source


class TestSingleFileCli:
    def test_the_normalized_copy_is_written(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        assert (out / "normalized_data.csv").is_file()

    def test_the_original_output_is_not_normalized(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        clean = pd.read_csv(out / "clean_data.csv")
        assert clean.loc[0, "address"] == "123 north maple ave., springfield, il 62704"
        assert clean.loc[0, "amount"] == "€1,000.00"

    def test_addresses_are_canonicalised(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        normalized = pd.read_csv(out / "normalized_data.csv")
        assert normalized.loc[0, "address"] == "123 N Maple Avenue, Springfield, IL 62704"
        assert normalized.loc[1, "address"] == "456 S Oak Street, Springfield, IL 62704"

    def test_amounts_are_converted(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        normalized = pd.read_csv(out / "normalized_data.csv")
        assert normalized.loc[0, "amount"] == pytest.approx(1080.0)
        assert normalized.loc[1, "amount"] == pytest.approx(635.0)

    def test_every_conversion_records_its_rate_and_date(self, home, case, tmp_path):
        config, source = case
        out = tmp_path / "out"
        main(["-i", str(source), "-c", str(config), "-o", str(out)])
        conversions = pd.read_csv(out / "currency_conversions.csv")
        assert set(conversions["from"]) == {"EUR", "GBP"}
        assert set(conversions["as_of"]) == {"2026-01-15"}
        assert conversions["converted"].all()

    def test_the_line_is_printed(self, home, case, tmp_path, capsys):
        config, source = case
        main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        out = capsys.readouterr().out
        assert "Normalization:" in out
        assert "2 address(es) canonicalised" in out

    def test_a_block_less_config_writes_nothing_extra(self, home, tmp_path):
        source = tmp_path / "orders.csv"
        source.write_text(ORDERS, encoding="utf-8")
        out = tmp_path / "out"
        main(["-i", str(source), "-c", "hubspot", "-o", str(out)])
        assert not (out / "normalized_data.csv").exists()
        assert not (out / "currency_conversions.csv").exists()

    def test_a_malformed_block_fails_the_run_cleanly(self, home, tmp_path, capsys):
        config = tmp_path / "bad.yaml"
        config.write_text(
            "crm: X\nfields: []\nnormalization:\n  nope: 1\n", encoding="utf-8"
        )
        source = tmp_path / "orders.csv"
        source.write_text(ORDERS, encoding="utf-8")
        code = main(["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")])
        assert code == 2
        assert "Invalid normalization configuration" in capsys.readouterr().err


class TestBatchCli:
    @pytest.fixture
    def inbox(self, case, tmp_path):
        _, source = case
        folder = tmp_path / "inbox"
        folder.mkdir()
        shutil.copy(source, folder / "a.csv")
        shutil.copy(source, folder / "b.csv")
        return folder

    def test_each_file_gets_a_normalized_copy(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        assert (out / "a" / "normalized_data.csv").is_file()
        assert (out / "b" / "normalized_data.csv").is_file()

    def test_the_summary_counts_the_work(self, home, case, inbox, tmp_path):
        config, _ = case
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", str(config), "--out", str(out)])
        summary = pd.read_csv(out / "summary.csv")
        assert "addresses_normalised" in summary.columns
        assert "amounts_converted" in summary.columns
        assert summary["addresses_normalised"].tolist() == [2, 2]
        assert summary["amounts_converted"].tolist() == [2, 2]

    def test_a_block_less_template_writes_nothing_extra(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)])
        assert not (out / "a" / "normalized_data.csv").exists()
        summary = pd.read_csv(out / "summary.csv")
        assert summary["addresses_normalised"].tolist() == [0, 0]
