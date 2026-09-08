import json

import pytest

from cutoffguard import TemporalRecord, audit_records
from cutoffguard.cli import main
from cutoffguard.errors import InputFormatError
from cutoffguard.io import load_csv, load_jsonl
from cutoffguard.records import parse_ts
from cutoffguard.report import render_json


def record(
    record_id: str, observed: str, available: str | None = None
) -> TemporalRecord:
    return TemporalRecord.from_dict(
        {"id": record_id, "observed_at": observed, "available_at": available}
    )


def test_structured_finding_and_counts_are_present():
    report = audit_records(
        [record("x", "2024-01-02T00:00:00Z", "2024-01-03T00:00:00Z")],
        "2024-01-01T00:00:00Z",
    )
    item = report.to_dict()
    assert item["schema_version"] == "1.0"
    assert item["finding_counts"] == {
        "FUTURE_OBSERVATION": 1,
        "POST_CUTOFF_AVAILABILITY": 1,
    }
    assert item["findings"][0]["category"] == "availability"
    assert item["findings"][0]["field"] == "observed_at"


def test_finding_order_is_deterministic():
    values = [
        record("b", "2024-01-02T00:00:00Z"),
        record("a", "2024-01-02T00:00:00Z"),
    ]
    first = render_json(audit_records(values, "2024-01-01T00:00:00Z"))
    second = render_json(audit_records(values, "2024-01-01T00:00:00Z"))
    assert first == second
    assert json.loads(first)["findings"][0]["record_id"] == "a"


def test_cutoff_errors_use_expected_error_type():
    with pytest.raises(InputFormatError, match="explicit UTC offset"):
        parse_ts("2024-01-01T00:00:00")


def test_jsonl_invalid_line(tmp_path):
    path = tmp_path / "x.jsonl"
    path.write_text(
        '{"id":"a","observed_at":"2024-01-01T00:00:00Z"}\n[1]\n', encoding="utf-8"
    )
    with pytest.raises(
        InputFormatError, match=r"x.jsonl:2: record must be a JSON object"
    ):
        load_jsonl(path)


def test_jsonl_bad_json_line(tmp_path):
    path = tmp_path / "x.jsonl"
    path.write_text("{bad}\n", encoding="utf-8")
    with pytest.raises(InputFormatError, match=r"x.jsonl:1: invalid JSON"):
        load_jsonl(path)


def test_csv_bom_and_empty_file(tmp_path):
    path = tmp_path / "records.csv"
    path.write_text("\ufeffid,observed_at\na,2024-01-01T00:00:00Z\n", encoding="utf-8")
    assert len(load_csv(path)) == 1
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    assert load_csv(empty) == []


def test_csv_missing_header(tmp_path):
    path = tmp_path / "records.csv"
    path.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(InputFormatError, match="missing CSV header fields"):
        load_csv(path)


def test_cli_invalid_input_is_exit_four_without_traceback(tmp_path, capsys):
    path = tmp_path / "bad.txt"
    path.write_text("anything", encoding="utf-8")
    assert main(["audit", str(path), "--cutoff", "2024-01-01T00:00:00Z"]) == 4
    captured = capsys.readouterr()
    assert "CutoffGuardError" in captured.err
    assert "Traceback" not in captured.err


def test_cli_review_and_fail_codes(tmp_path):
    review = tmp_path / "review.jsonl"
    review.write_text(
        '{"id":"a","observed_at":"2024-01-01T00:00:00Z"}\n', encoding="utf-8"
    )
    assert main(["audit", str(review), "--cutoff", "2024-01-02T00:00:00Z"]) == 1
    fail = tmp_path / "fail.jsonl"
    fail.write_text(
        '{"id":"a","observed_at":"2024-01-03T00:00:00Z"}\n', encoding="utf-8"
    )
    assert main(["audit", str(fail), "--cutoff", "2024-01-02T00:00:00Z"]) == 2


def test_cli_debug_can_show_traceback_for_invalid_input(tmp_path, capsys):
    path = tmp_path / "bad.txt"
    path.write_text("anything", encoding="utf-8")
    assert (
        main(["--debug", "audit", str(path), "--cutoff", "2024-01-01T00:00:00Z"]) == 4
    )
    assert "Traceback" in capsys.readouterr().err
