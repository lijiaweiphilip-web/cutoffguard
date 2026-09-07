from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def parse_ts(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        dt = value
    else:
        text = value.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    if dt is None:
        return None
    if dt.tzinfo is None:
        raise ValueError("timestamps must include an explicit UTC offset")
    return dt.astimezone(timezone.utc)

@dataclass(frozen=True)
class TemporalRecord:
    id: str
    observed_at: datetime
    available_at: datetime | None = None
    label_available_at: datetime | None = None
    revised_at: datetime | None = None
    value: Any = None
    source: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TemporalRecord:
        if not d.get("id"):
            raise ValueError("record id is required")
        if "observed_at" not in d:
            raise ValueError("observed_at is required")
        observed_at = parse_ts(d["observed_at"])
        if observed_at is None:
            raise ValueError("observed_at is required")
        return cls(
            id=str(d["id"]),
            observed_at=observed_at,
            available_at=parse_ts(d.get("available_at")),
            label_available_at=parse_ts(d.get("label_available_at")),
            revised_at=parse_ts(d.get("revised_at")),
            value=d.get("value"),
            source=d.get("source"),
        )
