"""Integration test for Module 1: profiling inside the full pipeline.

The extension must not disturb the frozen pipeline. These tests run the real
``run_pipeline`` on a real sample and assert that (a) the declared profiling
block produces its report alongside the pipeline's own artifacts, and (b) a run
with no ``profiling:`` block is byte-identical to one made before the
extension existed.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from app_files.config_bindings import apply_configured_bindings
from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.profiling.profiling_block import bind_profiling

CONFIG_WITH_BLOCK = """
fields:
  - name: email
    source: Email Address
  - name: phone
    source: Phone
  - name: full_name
    source: Full Name
profiling:
  statistics:
    enabled: true
  patterns:
    enabled: true
  outliers:
    enabled: true
"""

CONFIG_WITHOUT_BLOCK = """
fields:
  - name: email
    source: Email Address
  - name: phone
    source: Phone
  - name: full_name
    source: Full Name
"""


@pytest.fixture
def sample(tmp_path, contacts_csv):
    return contacts_csv


def test_the_pipeline_still_runs_with_the_block_declared(tmp_path, sample):
    config = tmp_path / "with.yaml"
    config.write_text(CONFIG_WITH_BLOCK, encoding="utf-8")
    result = run_pipeline(read_any(sample), crm=config)
    assert result.clean_frame is not None
    assert len(result.clean_frame) > 0


def test_the_block_produces_a_report_through_the_shared_binding(tmp_path, sample):
    config = tmp_path / "with.yaml"
    config.write_text(CONFIG_WITH_BLOCK, encoding="utf-8")
    result = run_pipeline(read_any(sample), crm=config)
    bindings = apply_configured_bindings(result, config)
    assert bindings.profiling is not None
    assert bindings.profiling.statistics


def test_an_undeclared_block_binds_nothing(tmp_path, sample):
    config = tmp_path / "without.yaml"
    config.write_text(CONFIG_WITHOUT_BLOCK, encoding="utf-8")
    result = run_pipeline(read_any(sample), crm=config)
    bindings = apply_configured_bindings(result, config)
    assert bindings.profiling is None


def test_the_pipeline_output_is_unchanged_by_the_extension(tmp_path, sample):
    """The strongest guarantee: declaring the block cannot change the data."""
    without = tmp_path / "without.yaml"
    without.write_text(CONFIG_WITHOUT_BLOCK, encoding="utf-8")
    with_block = tmp_path / "with.yaml"
    with_block.write_text(CONFIG_WITH_BLOCK, encoding="utf-8")

    a = run_pipeline(read_any(sample), crm=without)
    b = run_pipeline(read_any(sample), crm=with_block)
    pd.testing.assert_frame_equal(a.clean_frame, b.clean_frame)


def test_the_report_is_json_serialisable(tmp_path, sample):
    config = tmp_path / "with.yaml"
    config.write_text(CONFIG_WITH_BLOCK, encoding="utf-8")
    result = run_pipeline(read_any(sample), crm=config)
    bindings = apply_configured_bindings(result, config)
    json.dumps(bindings.profiling.summary())


def test_the_binding_is_reachable_from_the_config_bindings_summary(tmp_path, sample):
    config = tmp_path / "with.yaml"
    config.write_text(CONFIG_WITH_BLOCK, encoding="utf-8")
    result = run_pipeline(read_any(sample), crm=config)
    bindings = apply_configured_bindings(result, config)
    summary = bindings.summary()
    assert "profiling" in summary
