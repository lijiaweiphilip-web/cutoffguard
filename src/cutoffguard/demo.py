from __future__ import annotations

from .audit import audit_records
from .records import TemporalRecord, parse_ts


def demo_records():
    return [
        TemporalRecord(
            "gdp_q1",
            parse_ts("2024-03-31T00:00:00Z"),
            parse_ts("2024-04-25T12:30:00Z"),
            source="illustrative_release_calendar",
        ),
        TemporalRecord(
            "label_5d",
            parse_ts("2024-04-01T00:00:00Z"),
            parse_ts("2024-04-01T00:00:00Z"),
            parse_ts("2024-04-08T00:00:00Z"),
            source="derived_label",
        ),
    ]


def run_demo():
    return audit_records(demo_records(), "2024-04-15T00:00:00Z")
