"""The ``dedupe:`` block in a config must bind in a run.

``FuzzyRule.from_dict`` was written to be read from a config, but no run read
one — the module had zero callers outside its own package. These tests drive
the binding directly; the integration module drives it through the real CLI.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.dedupe.binding import (
    apply_configured_dedupe,
    apply_dedupe,
    declared_dedupe_rules,
    dedupe_block,
)
from app_files.dedupe.engine import DedupeConfigError, FuzzyRule


@pytest.fixture
def contacts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "first_name": ["John", "Jon", "Jane", "Janet"],
            "last_name": ["Smith", "Smith", "Doe", "Doe"],
        }
    )


def _write_config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "crm.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_block_is_none_without_the_key(tmp_path):
    path = _write_config(tmp_path, "crm: X\nfields: []\n")
    assert dedupe_block(path) is None


def test_configured_dedupe_is_none_without_the_block(tmp_path, contacts):
    path = _write_config(tmp_path, "crm: X\n")
    assert apply_configured_dedupe(contacts, path) is None


def test_an_explicit_disable_is_honoured(tmp_path, contacts):
    path = _write_config(tmp_path, "crm: X\ndedupe:\n  enabled: false\n")
    assert apply_configured_dedupe(contacts, path) is None


def test_a_single_rule_shorthand_is_accepted(tmp_path, contacts):
    path = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rule:\n    columns: [first_name, last_name]\n    threshold: 0.85\n",
    )
    rules = declared_dedupe_rules(path)
    assert len(rules) == 1
    assert rules[0].threshold == 0.85


def test_the_spec_threshold_pair(tmp_path, contacts):
    """John/Jon Smith merges at 0.85; at 0.95 the pair is distinct."""
    low = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rules:\n    - {columns: [first_name, last_name], threshold: 0.85}\n",
    )
    outcome = apply_configured_dedupe(contacts, low)
    assert outcome is not None
    assert outcome.duplicates_removed == 2

    high = tmp_path / "high.yaml"
    high.write_text(
        "crm: X\ndedupe:\n  rules:\n    - {columns: [first_name, last_name], threshold: 0.95}\n",
        encoding="utf-8",
    )
    # Jane/Janet score 0.96 and still merge at 0.95; the John/Jon pair (0.933)
    # is what the spec's 0.95 case is about, so isolate it.
    pair = contacts.iloc[:2]
    outcome = apply_configured_dedupe(pair, high)
    assert outcome is not None
    assert outcome.duplicates_removed == 0


def test_the_input_frame_is_untouched(tmp_path, contacts):
    path = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rules:\n    - {columns: [first_name, last_name], threshold: 0.85}\n",
    )
    before = contacts.copy(deep=True)
    apply_configured_dedupe(contacts, path)
    pd.testing.assert_frame_equal(contacts, before)


def test_the_merge_log_records_the_evidence(tmp_path, contacts):
    path = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rules:\n    - {columns: [first_name, last_name], threshold: 0.85}\n",
    )
    outcome = apply_configured_dedupe(contacts, path)
    assert outcome is not None
    merges = outcome.merges_frame()
    assert list(merges.columns) == ["kept_row", "dropped_row", "score", "metric", "reason"]
    assert merges.iloc[0]["kept_row"] == 0
    assert merges.iloc[0]["dropped_row"] == 1
    assert merges.iloc[0]["metric"] == "jaro_winkler"


def test_levenshtein_is_selectable(tmp_path, contacts):
    path = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rules:\n"
        "    - {columns: [first_name, last_name], metric: levenshtein, threshold: 0.85}\n",
    )
    rules = declared_dedupe_rules(path)
    assert rules[0].metric == "levenshtein"


def test_rules_apply_in_order(tmp_path):
    frame = pd.DataFrame({"name": ["Alpha", "Alfa", "Beta", "Betta"]})
    outcome = apply_dedupe(
        frame,
        [
            FuzzyRule(columns=["name"], threshold=0.8),
            FuzzyRule(columns=["name"], threshold=0.8),
        ],
    )
    assert outcome.duplicates_removed == 2
    assert len(outcome.rules) == 2


def test_unknown_block_keys_raise(tmp_path, contacts):
    path = _write_config(tmp_path, "crm: X\ndedupe:\n  rules: []\n  nope: 1\n")
    with pytest.raises(DedupeConfigError):
        apply_configured_dedupe(contacts, path)


def test_a_rule_without_columns_raises(tmp_path, contacts):
    path = _write_config(tmp_path, "crm: X\ndedupe:\n  rules:\n    - {threshold: 0.9}\n")
    with pytest.raises(DedupeConfigError):
        apply_configured_dedupe(contacts, path)


def test_the_summary_reports_the_work(tmp_path, contacts):
    path = _write_config(
        tmp_path,
        "crm: X\ndedupe:\n  rules:\n    - {columns: [first_name, last_name], threshold: 0.85}\n",
    )
    outcome = apply_configured_dedupe(contacts, path)
    assert outcome is not None
    summary = outcome.summary()
    assert summary["rows_in"] == 4
    assert summary["rows_out"] == 2
    assert summary["duplicates_removed"] == 2
    assert summary["rules"] == 1
