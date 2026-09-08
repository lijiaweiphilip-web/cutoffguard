from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .errors import InputFormatError


def parse_ts(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        dt = value
    else:
        if not isinstance(value, str):
            raise InputFormatError("timestamp must be an ISO-8601 string or datetime")
        text = value.strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError as exc:
            raise InputFormatError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if dt is None:
        return None
    if dt.tzinfo is None:
        raise InputFormatError("timestamps must include an explicit UTC offset")
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
        if not isinstance(d, Mapping):
            raise InputFormatError("record must be a JSON object")
        if not d.get("id"):
            raise InputFormatError("record id is required")
        if "observed_at" not in d:
            raise InputFormatError("observed_at is required")
        observed_at = parse_ts(d["observed_at"])
        if observed_at is None:
            raise InputFormatError("observed_at is required")
        return cls(
            id=str(d["id"]),
            observed_at=observed_at,
            available_at=parse_ts(d.get("available_at")),
            label_available_at=parse_ts(d.get("label_available_at")),
            revised_at=parse_ts(d.get("revised_at")),
            value=d.get("value"),
            source=d.get("source"),
        )
