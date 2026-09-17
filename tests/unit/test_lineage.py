"""Unit tests for the lineage tracker and report writer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app_files.lineage import (
    EVENT_COLUMNS,
    LINEAGE_ID,
    LineageTracker,
    attach_lineage_ids,
    lineage_summary,
    render_lineage_html,
    strip_lineage_ids,
    write_lineage_report,
)


def _tracker() -> LineageTracker:
    tracker = LineageTracker()
    tracker.record(
        field_name="createdate", before="31-Dec-24", after="2024-12-31",
        action="clean:date_iso", source_row=0, output_row=0,
    )
    tracker.record(
        field_name="email", before="ANN@X.COM", after="ann@x.com",
        action="map:lower_case", source_row=0, output_row=0,
    )
    return tracker


def test_tracker_records_one_row_per_transformation():
    tracker = _tracker()
    assert tracker.total_events == 2
    frame = tracker.to_frame()
    assert list(frame.columns) == EVENT_COLUMNS
    assert len(frame) == 2


def test_recorded_event_keeps_before_and_after():
    frame = _tracker().to_frame()
    row = frame.iloc[0]
    assert row["field"] == "createdate"
    assert row["before"] == "31-Dec-24"
    assert row["after"] == "2024-12-31"
    assert row["action"] == "clean:date_iso"


def test_unchanged_values_are_not_recorded():
    tracker = LineageTracker()
    tracker.record(field_name="email", before="a@x.com", after="a@x.com", action="noop")
    assert tracker.total_events == 0


def test_blanks_are_compared_consistently():
    tracker = LineageTracker()
    # None and "" are both "blank", so no spurious event.
    tracker.record(field_name="phone", before=None, after="", action="noop")
    assert tracker.total_events == 0


def test_actions_are_counted():
    tracker = _tracker()
    assert tracker.actions() == {"clean:date_iso": 1, "map:lower_case": 1}


def test_empty_tracker_yields_empty_frame_with_columns():
    frame = LineageTracker().to_frame()
    assert frame.empty
    assert list(frame.columns) == EVENT_COLUMNS


def test_record_frame_diff_captures_every_changed_cell():
    before = pd.DataFrame({"email": ["A@X.com", "B@X.com"]})
    after = pd.DataFrame({"email": ["a@x.com", "b@x.com"]})
    tracker = LineageTracker()
    count = tracker.record_frame_diff(before, after, "email", "map:lower_case")
    assert count == 2
    assert tracker.total_events == 2


def test_record_frame_diff_ignores_identical_frames():
    frame = pd.DataFrame({"email": ["a@x.com", "b@x.com"]})
    tracker = LineageTracker()
    assert tracker.record_frame_diff(frame, frame.copy(), "email", "noop") == 0


def test_record_removed_rows_logs_dropped_reason():
    frame = pd.DataFrame({LINEAGE_ID: [0, 1, 2, 3], "email": ["a", "a", "b", "b"]})
    tracker = LineageTracker()
    tracker.record_removed_rows(frame, [2, 3], action="removed_duplicate")
    log = tracker.to_frame()
    assert len(log) == 2
    assert set(log["action"]) == {"removed_duplicate"}
    # Dropped rows keep their identity so they can still be traced.
    assert set(log["before"]) == {"row 2", "row 3"}


def test_record_removed_rows_without_ids_is_a_no_op():
    tracker = LineageTracker()
    tracker.record_removed_rows(pd.DataFrame({"a": [1]}), [], action="removed_duplicate")
    assert tracker.total_events == 0


def test_attach_and_strip_lineage_id_round_trip():
    frame = pd.DataFrame({"email": ["a@x.com", "b@x.com"]})
    tagged = attach_lineage_ids(frame)
    assert LINEAGE_ID in tagged.columns
    restored = strip_lineage_ids(tagged)
    assert LINEAGE_ID not in restored.columns
    pd.testing.assert_frame_equal(restored, frame)


def test_lineage_ids_survive_dedup_so_events_still_match():
    frame = attach_lineage_ids(pd.DataFrame({"email": ["a@x.com", "a@x.com", "b@x.com"]}))
    deduped = frame.drop_duplicates(subset=["email"])
    assert len(deduped) == 2
    # The surviving row keeps its original identity rather than being renumbered.
    assert deduped.iloc[0][LINEAGE_ID] == frame.iloc[0][LINEAGE_ID]


def test_source_row_can_be_traced_from_output_row():
    tracker = _tracker()
    events = tracker.events_for_output_row(0)
    assert len(events) == 2
    assert set(events["field"]) == {"createdate", "email"}


def test_lineage_summary_reports_counts():
    summary = lineage_summary(_tracker())
    assert summary["total_events"] == 2
    assert summary["rows_touched"] == 1
    assert summary["actions"]["clean:date_iso"] == 1


def test_report_is_written_as_csv(tmp_path: Path):
    path = write_lineage_report(_tracker(), tmp_path / "lineage_report.csv")
    assert path.exists()
    frame = pd.read_csv(path)
    assert list(frame.columns) == EVENT_COLUMNS
    assert len(frame) == 2


def test_report_written_for_empty_tracker_is_still_valid_csv(tmp_path: Path):
    path = write_lineage_report(LineageTracker(), tmp_path / "empty.csv")
    assert path.exists()
    frame = pd.read_csv(path)
    assert frame.empty
    assert list(frame.columns) == EVENT_COLUMNS


def test_rendered_html_mentions_the_events():
    html = render_lineage_html(_tracker())
    assert "Transformation lineage" in html
    assert "createdate" in html
    assert "2 events" in html


def test_disabled_tracker_records_nothing():
    tracker = LineageTracker(enabled=False)
    tracker.record(field_name="a", before="1", after="2", action="x")
    assert tracker.total_events == 0