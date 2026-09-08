from datetime import datetime, timezone

import pytest

from cutoffguard.records import TemporalRecord, parse_ts


def test_parse_z():
    assert parse_ts("2024-01-01T00:00:00Z").utcoffset().total_seconds() == 0


def test_naive_rejected():
    with pytest.raises(ValueError):
        parse_ts("2024-01-01T00:00:00")


def test_record_requires_id():
    with pytest.raises(ValueError):
        TemporalRecord.from_dict({"id": "", "observed_at": "2024-01-01T00:00:00Z"})


@pytest.mark.parametrize("bad_id", [1, True, 1.5, None, "   "])
def test_record_rejects_non_string_or_blank_ids(bad_id):
    with pytest.raises(ValueError, match="non-empty string"):
        TemporalRecord.from_dict({"id": bad_id, "observed_at": "2024-01-01T00:00:00Z"})


def test_record_rejects_non_string_source():
    with pytest.raises(ValueError, match="source must be a string or null"):
        TemporalRecord.from_dict(
            {
                "id": "a",
                "observed_at": "2024-01-01T00:00:00Z",
                "source": 123,
            }
        )


def test_direct_construction_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="explicit UTC offset"):
        TemporalRecord("a", datetime(2024, 1, 1))


def test_direct_construction_normalizes_timestamps_to_utc():
    record = TemporalRecord(
        "a",
        datetime(2024, 1, 1, 8, tzinfo=timezone.utc),
        datetime(2024, 1, 1, 10, tzinfo=timezone.utc),
    )
    assert record.observed_at.tzinfo == timezone.utc
    assert record.available_at.tzinfo == timezone.utc


def test_record_requires_observed_at():
    with pytest.raises(ValueError, match="observed_at is required"):
        TemporalRecord.from_dict({"id": "a"})
