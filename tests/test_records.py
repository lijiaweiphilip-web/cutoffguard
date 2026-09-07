import pytest

from cutoffguard.records import TemporalRecord, parse_ts


def test_parse_z(): assert parse_ts("2024-01-01T00:00:00Z").utcoffset().total_seconds()==0
def test_naive_rejected():
    with pytest.raises(ValueError): parse_ts("2024-01-01T00:00:00")
def test_record_requires_id():
    with pytest.raises(ValueError): TemporalRecord.from_dict({"id":"","observed_at":"2024-01-01T00:00:00Z"})

def test_record_requires_observed_at():
    with pytest.raises(ValueError, match="observed_at is required"):
        TemporalRecord.from_dict({"id": "a"})
