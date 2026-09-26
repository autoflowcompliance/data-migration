"""Layer 4 — cross-field rules and rule versioning/sandbox."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.rules import (
    CrossFieldRule,
    CrossFieldRuleError,
    RuleVersionError,
    SandboxStore,
    load_cross_field_rules,
    run_cross_field_rules,
)

FRAME = pd.DataFrame(
    {
        "open_date": ["2024-03-01", "2024-01-01", "2024-05-01"],
        "close_date": ["2024-03-05", "2023-12-01", "2024-05-10"],
        "total": [100.0, 50.0, 200.0],
        "subtotal": [60.0, 20.0, 150.0],
        "tax": [40.0, 30.0, 50.0],
    }
)


def compare_rule(**overrides) -> CrossFieldRule:
    payload = {"name": "cmp", "type": "compare", "fields": ["a", "b"], "operator": "<"}
    payload.update(overrides)
    return CrossFieldRule.from_dict(payload)


class TestCrossFieldSchema:
    def test_a_valid_rule_round_trips(self):
        rule = compare_rule()
        assert rule.as_dict()["operator"] == "<"
        assert rule.describe() == "a < b"

    def test_missing_operator_is_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="needs an 'operator'"):
            CrossFieldRule.from_dict({"name": "x", "type": "compare", "fields": ["a", "b"]})

    def test_unknown_operator_is_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="unknown operator"):
            compare_rule(operator="~")

    def test_unknown_type_is_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="unknown type"):
            CrossFieldRule.from_dict({"name": "x", "type": "nope", "fields": ["a", "b"]})

    def test_fewer_than_two_fields_is_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="at least two columns"):
            compare_rule(fields=["a"])

    def test_sum_equals_needs_a_total_and_two_parts(self):
        with pytest.raises(CrossFieldRuleError, match="total plus"):
            CrossFieldRule.from_dict(
                {"name": "x", "type": "sum_equals", "fields": ["total", "part"]}
            )

    def test_a_missing_name_is_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="needs a name"):
            CrossFieldRule.from_dict({"type": "compare", "fields": ["a", "b"], "operator": "<"})

    def test_unknown_keys_are_rejected(self):
        with pytest.raises(CrossFieldRuleError, match="unknown keys"):
            compare_rule(surprise=1)

    def test_the_config_block_is_read(self):
        rules = load_cross_field_rules({"cross_field": [compare_rule().as_dict()]})
        assert rules[0].name == "cmp"

    def test_an_empty_config_block_reads_as_no_rules(self):
        assert load_cross_field_rules({}) == []


class TestDateOrder:
    def test_a_close_date_before_an_open_date_is_flagged_on_the_right_row(self):
        rule = CrossFieldRule.from_dict(
            {"name": "close_after_open", "type": "date_order",
             "fields": ["open_date", "close_date"]}
        )
        result = run_cross_field_rules(FRAME, [rule])
        assert result.total_failures == 1
        assert result.issues[0].row == 1
        assert result.issues[0].check == "cross_field:close_after_open"

    def test_a_blank_date_is_skipped_not_failed(self):
        frame = pd.DataFrame(
            {"open_date": [None], "close_date": ["2024-01-01"]}
        )
        rule = CrossFieldRule.from_dict(
            {"name": "d", "type": "date_order", "fields": ["open_date", "close_date"]}
        )
        assert run_cross_field_rules(frame, [rule]).total_failures == 0

    def test_unparseable_dates_are_skipped(self):
        frame = pd.DataFrame({"open_date": ["not-a-date"], "close_date": ["2024-01-01"]})
        rule = CrossFieldRule.from_dict(
            {"name": "d", "type": "date_order", "fields": ["open_date", "close_date"]}
        )
        assert run_cross_field_rules(frame, [rule]).total_failures == 0


class TestSumEquals:
    def test_a_mismatched_total_is_flagged(self):
        rule = CrossFieldRule.from_dict(
            {"name": "total_parts", "type": "sum_equals",
             "fields": ["total", "subtotal", "tax"], "tolerance": 0.01}
        )
        frame = FRAME.copy()
        frame.loc[1, "total"] = 999.0  # 20 + 30 != 999
        result = run_cross_field_rules(frame, [rule])
        assert result.total_failures == 1
        assert result.issues[0].row == 1

    def test_a_matching_total_is_not_flagged(self):
        rule = CrossFieldRule.from_dict(
            {"name": "total_parts", "type": "sum_equals",
             "fields": ["total", "subtotal", "tax"], "tolerance": 0.01}
        )
        assert run_cross_field_rules(FRAME, [rule]).total_failures == 0

    def test_tolerance_forgives_small_rounding(self):
        frame = pd.DataFrame({"total": [100.004], "a": [60.0], "b": [40.0]})
        rule = CrossFieldRule.from_dict(
            {"name": "s", "type": "sum_equals", "fields": ["total", "a", "b"], "tolerance": 0.01}
        )
        assert run_cross_field_rules(frame, [rule]).total_failures == 0

    def test_a_blank_part_skips_the_row(self):
        frame = pd.DataFrame({"total": [100.0], "a": [None], "b": [40.0]})
        rule = CrossFieldRule.from_dict(
            {"name": "s", "type": "sum_equals", "fields": ["total", "a", "b"]}
        )
        assert run_cross_field_rules(frame, [rule]).total_failures == 0


class TestCompare:
    @pytest.mark.parametrize(
        "operator,left,right,fails",
        [("<", 1, 2, False), ("<", 2, 1, True), ("<=", 2, 2, False),
         ("==", 2, 2, False), ("!=", 2, 2, True), (">", 3, 2, False),
         (">=", 2, 3, True)],
    )
    def test_each_operator(self, operator, left, right, fails):
        frame = pd.DataFrame({"a": [left], "b": [right]})
        rule = compare_rule(operator=operator)
        assert bool(run_cross_field_rules(frame, [rule]).total_failures) is fails

    def test_a_currency_formatted_number_is_understood(self):
        frame = pd.DataFrame({"a": ["$1,200.50"], "b": ["1000"]})
        assert run_cross_field_rules(frame, [compare_rule(operator=">")]).total_failures == 0

    def test_a_non_numeric_value_skips_the_row(self):
        frame = pd.DataFrame({"a": ["abc"], "b": ["1"]})
        assert run_cross_field_rules(frame, [compare_rule(operator=">")]).total_failures == 0


class TestRuleSetSharing:
    def test_a_rule_with_an_absent_column_is_skipped_not_raised(self):
        result = run_cross_field_rules(pd.DataFrame({"x": [1]}), [compare_rule()])
        assert result.skipped_rules == ["cmp"]
        assert result.rules_run == 0

    def test_custom_message_is_used(self):
        frame = pd.DataFrame({"a": [5], "b": [1]})
        rule = compare_rule(operator="<", message="a must stay below b")
        assert run_cross_field_rules(frame, [rule]).issues[0].message == "a must stay below b"

    def test_summary_lists_run_and_failures(self):
        rule = CrossFieldRule.from_dict(
            {"name": "d", "type": "date_order", "fields": ["open_date", "close_date"]}
        )
        summary = run_cross_field_rules(FRAME, [rule]).summary()
        assert summary["rules_run"] == 1
        assert summary["failures_by_rule"] == {"d": 1}


@pytest.fixture
def store(tmp_path):
    return SandboxStore(tmp_path)


class TestSandboxPromotion:
    def _rule(self) -> CrossFieldRule:
        return CrossFieldRule.from_dict(
            {"name": "d", "type": "date_order", "fields": ["open_date", "close_date"]}
        )

    def test_a_version_starts_as_a_draft(self, store):
        version = store.save_version("rules", cross_field=[self._rule()])
        assert version.status == "draft"
        assert version.version == 1

    def test_version_numbers_increment(self, store):
        store.save_version("rules")
        store.save_version("rules")
        assert [v.version for v in store.history("rules")] == [1, 2]

    def test_no_rule_reaches_production_without_a_sandbox_run(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        with pytest.raises(RuleVersionError, match="no sandbox run"):
            store.promote("rules", 1)

    def test_a_sandbox_run_records_its_outcome(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        outcome = store.sandbox_run("rules", 1, [FRAME])
        assert outcome.frames_tested == 1
        assert outcome.failures == 1
        assert outcome.failures_by_rule == {"d": 1}

    def test_a_version_can_be_promoted_after_sandboxing(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        promoted = store.promote("rules", 1)
        assert promoted.status == "production"
        assert store.production("rules").version == 1

    def test_promoting_a_new_version_supersedes_the_old(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        store.promote("rules", 1)
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 2, [FRAME])
        store.promote("rules", 2)
        statuses = [(v.version, v.status) for v in store.history("rules")]
        assert statuses == [(1, "superseded"), (2, "production")]

    def test_the_sandbox_run_persists_to_disk(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        assert SandboxStore(store.root).history("rules")[0].sandbox_runs

    def test_promotion_persists_across_reopened_stores(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        store.promote("rules", 1)
        assert SandboxStore(store.root).production("rules").version == 1

    def test_an_unknown_version_is_an_error(self, store):
        with pytest.raises(RuleVersionError, match="No version"):
            store.promote("rules", 9)

    def test_a_sandbox_run_never_promotes(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        assert store.production("rules") is None

    def test_multiple_frames_accumulate(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        outcome = store.sandbox_run("rules", 1, [FRAME, FRAME])
        assert outcome.frames_tested == 2
        assert outcome.failures == 2

    def test_skipped_rules_are_reported(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        outcome = store.sandbox_run("rules", 1, [pd.DataFrame({"x": [1]})])
        assert outcome.skipped_rules == ["d"]


class TestRollback:
    def _rule(self, name: str = "d") -> CrossFieldRule:
        return CrossFieldRule.from_dict(
            {"name": name, "type": "date_order", "fields": ["open_date", "close_date"]}
        )

    def test_rollback_restores_the_earlier_rules_as_a_new_version(self, store):
        store.save_version("rules", cross_field=[self._rule("first")])
        store.sandbox_run("rules", 1, [FRAME])
        store.promote("rules", 1)
        store.save_version("rules", cross_field=[self._rule("second")])
        store.sandbox_run("rules", 2, [FRAME])
        store.promote("rules", 2)

        restored = store.rollback_to("rules", 1)
        assert restored.version == 3
        assert restored.status == "production"
        assert restored.cross_field[0]["name"] == "first"

    def test_rollback_preserves_the_version_it_replaced(self, store):
        store.save_version("rules", cross_field=[self._rule("first")])
        store.sandbox_run("rules", 1, [FRAME])
        store.promote("rules", 1)
        store.save_version("rules", cross_field=[self._rule("second")])
        store.sandbox_run("rules", 2, [FRAME])
        store.promote("rules", 2)
        store.rollback_to("rules", 1)
        # Version 2 still exists, superseded rather than deleted.
        statuses = {v.version: v.status for v in store.history("rules")}
        assert statuses[2] == "superseded"
        assert statuses[3] == "production"

    def test_rollback_records_what_it_reverted_to(self, store):
        store.save_version("rules", cross_field=[self._rule()])
        store.sandbox_run("rules", 1, [FRAME])
        store.promote("rules", 1)
        restored = store.rollback_to("rules", 1)
        assert restored.sandbox_runs[0]["rollback_of"] == 1

    def test_rollback_of_an_unknown_version_is_an_error(self, store):
        with pytest.raises(RuleVersionError, match="No version"):
            store.rollback_to("rules", 7)


class TestSingleFieldRulesAlsoVersion:
    def test_the_single_field_rule_dataclass_can_be_stored(self, store):
        from app_files.rules import Rule

        version = store.save_version(
            "rules", single_field=[Rule(name="r", field="email", type="required")]
        )
        stored = store.history("rules")[0]
        assert stored.single_field[0]["name"] == "r"
        assert version.rule_count == 1
