"""Layer 19 — the schema drift gate.

The registry tests in ``test_mapper_learning`` prove drift can be *reported*.
These prove the gate acts on it: a changed source is judged against the target
mapping and a blocked verdict stops the run before it starts.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from app_files.drift import (
    BLOCK,
    OK,
    WARN,
    DriftBlocked,
    DriftGate,
    SchemaRegistry,
    schema_of,
)


@pytest.fixture
def gate(tmp_path):
    return DriftGate(SchemaRegistry(path=tmp_path / "schemas.json"))


def source_frame() -> pd.DataFrame:
    """A shape that satisfies the shipped hubspot config's required fields."""
    return pd.DataFrame(
        {
            "Email Address": ["alice@example.com", "bob@example.com"],
            "First Name": ["Alice", "Bob"],
            "Phone": ["+14155552671", "+14155552672"],
            "Company": ["Acme", "Globex"],
        }
    )


# ------------------------------------------------------------------- verdicts


class TestVerdicts:
    def test_an_unknown_source_is_never_blocked(self, gate):
        decision = gate.check("never-seen", source_frame(), "hubspot")
        assert decision.verdict == OK
        assert decision.proceed is True
        assert not decision.has_drift
        assert any("first run" in reason for reason in decision.reasons)

    def test_an_unchanged_source_reports_no_drift(self, gate):
        frame = source_frame()
        gate.remember("crm", frame)
        decision = gate.check("crm", frame, "hubspot")
        assert decision.verdict == OK
        assert not decision.has_drift

    def test_an_added_column_warns_but_proceeds(self, gate):
        gate.remember("crm", source_frame())
        grown = source_frame()
        grown["Loyalty Tier"] = ["gold", "silver"]
        decision = gate.check("crm", grown, "hubspot")
        assert decision.verdict == WARN
        assert decision.proceed is True
        assert "Loyalty Tier" in decision.drift.added
        assert any("unmapped" in reason for reason in decision.reasons)

    def test_removing_a_required_source_column_blocks(self, gate):
        gate.remember("crm", source_frame())
        shrunk = source_frame().drop(columns=["Email Address"])
        decision = gate.check("crm", shrunk, "hubspot")
        assert decision.verdict == BLOCK
        assert decision.proceed is False
        assert "Email Address" in decision.blocked_columns

    def test_removing_an_unmapped_column_only_warns(self, gate):
        frame = source_frame()
        frame["Internal Note"] = ["x", "y"]
        gate.remember("crm", frame)
        without = frame.drop(columns=["Internal Note"])
        decision = gate.check("crm", without, "hubspot")
        assert decision.verdict == WARN
        assert decision.proceed is True

    def test_a_retype_is_a_warning_when_it_still_resolves(self, gate):
        gate.remember("crm", source_frame())
        # Phone goes from numeric-looking strings to true numbers: a retype the
        # mapping still resolves.
        retyped = source_frame()
        retyped["Phone"] = [14155552671, 14155552672]
        decision = gate.check("crm", retyped, "hubspot")
        assert decision.verdict in {WARN, OK}
        assert any("retyped" in reason for reason in decision.reasons)

    def test_a_rename_reports_add_and_remove_not_silence(self, gate):
        gate.remember("crm", source_frame())
        renamed = source_frame().rename(columns={"Phone": "Mobile Number"})
        decision = gate.check("crm", renamed, "hubspot")
        assert decision.has_drift
        assert "Mobile Number" in decision.drift.added or "Mobile Number" in decision.blocked_columns


class TestDecisionSurface:
    def test_blocked_columns_lists_the_source_column(self, gate):
        gate.remember("crm", source_frame())
        decision = gate.check("crm", source_frame().drop(columns=["First Name"]), "hubspot")
        assert decision.blocked_columns
        assert all(isinstance(column, str) for column in decision.blocked_columns)

    def test_decision_is_json_serialisable(self, gate):
        gate.remember("crm", source_frame())
        decision = gate.check("crm", source_frame().drop(columns=["Email Address"]), "hubspot")
        json.dumps(decision.as_dict())

    def test_summary_names_the_verdict(self, gate):
        gate.remember("crm", source_frame())
        grown = source_frame()
        grown["Extra"] = ["1", "2"]
        text = gate.check("crm", grown, "hubspot").summary()
        assert "attention" in text
        blocked = gate.check("crm", source_frame().drop(columns=["Email Address"]), "hubspot")
        assert "reviewed" in blocked.summary()


class TestGuardedRun:
    def test_a_clean_run_goes_through_and_remembers(self, gate):
        frame = source_frame()
        result, decision = gate.guarded_run("crm", frame, "hubspot", source_filename="c.csv")
        assert decision.verdict == OK
        assert result.validation.quality_score is not None
        # The schema is remembered so the next run has something to compare to.
        assert gate.last_schema("crm") is not None

    def test_a_blocked_run_never_reaches_the_pipeline(self, gate):
        gate.remember("crm", source_frame())
        shrunk = source_frame().drop(columns=["Email Address"])
        with pytest.raises(DriftBlocked) as caught:
            gate.guarded_run("crm", shrunk, "hubspot")
        assert caught.value.decision.verdict == BLOCK

    def test_a_blocked_run_does_not_overwrite_the_remembered_schema(self, gate):
        gate.remember("crm", source_frame())
        before = gate.last_schema("crm")
        shrunk = source_frame().drop(columns=["Email Address"])
        with pytest.raises(DriftBlocked):
            gate.guarded_run("crm", shrunk, "hubspot")
        assert gate.last_schema("crm") == before

    def test_a_warning_run_still_produces_output(self, gate):
        gate.remember("crm", source_frame())
        grown = source_frame()
        grown["Loyalty Tier"] = ["gold", "silver"]
        result, decision = gate.guarded_run("crm", grown, "hubspot", source_filename="c.csv")
        assert decision.verdict == WARN
        assert result.validation.quality_score is not None


class TestSchemaOf:
    def test_types_are_inferred_from_values(self):
        frame = pd.DataFrame(
            {"n": ["1", "2"], "f": ["1.5", "2.5"], "s": ["a", "b"], "d": ["2024-01-05", "2024-02-06"]}
        )
        types = schema_of(frame)
        assert types["n"] == "integer"
        assert types["f"] == "number"
        assert types["s"] == "string"
        assert types["d"] == "date"
