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

    def __post_init__(self) -> None:
        """Enforce the public record contract for every construction path.

        ``from_dict`` is not the only way callers can construct a record.  The
        frozen dataclass therefore validates and normalises values here as
        well, while deliberately refusing implicit identifier/source coercion.
        """
        if not isinstance(self.id, str) or not self.id.strip():
            raise InputFormatError("record id must be a non-empty string")
        if self.source is not None and not isinstance(self.source, str):
            raise InputFormatError("source must be a string or null")
        for field_name in (
            "observed_at",
            "available_at",
            "label_available_at",
            "revised_at",
        ):
            value = getattr(self, field_name)
            if value is None:
                if field_name == "observed_at":
                    raise InputFormatError("observed_at is required")
                continue
            if not isinstance(value, datetime):
                raise InputFormatError(f"{field_name} must be a datetime")
            if value.tzinfo is None:
                raise InputFormatError(
                    f"{field_name} must include an explicit UTC offset"
                )
            object.__setattr__(self, field_name, value.astimezone(timezone.utc))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TemporalRecord:
        if not isinstance(d, Mapping):
            raise InputFormatError("record must be a JSON object")
        if "id" not in d or not isinstance(d["id"], str) or not d["id"].strip():
            raise InputFormatError("record id must be a non-empty string")
        if "observed_at" not in d:
            raise InputFormatError("observed_at is required")
        observed_at = parse_ts(d["observed_at"])
        if observed_at is None:
            raise InputFormatError("observed_at is required")
        return cls(
            id=d["id"],
            observed_at=observed_at,
            available_at=parse_ts(d.get("available_at")),
            label_available_at=parse_ts(d.get("label_available_at")),
            revised_at=parse_ts(d.get("revised_at")),
            value=d.get("value"),
            source=d.get("source"),
        )
