from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime

from .records import TemporalRecord, parse_ts


@dataclass(frozen=True)
class AuditFinding:
    code: str
    record_id: str
    severity: str
    message: str

@dataclass(frozen=True)
class AuditReport:
    cutoff: datetime
    status: str
    findings: tuple[AuditFinding, ...]
    checked_records: int

    def to_dict(self):
        return {
            "cutoff": self.cutoff.isoformat(),
            "status": self.status,
            "checked_records": self.checked_records,
            "findings": [asdict(f) for f in self.findings],
            "assurance_boundary": (
                "No listed temporal violation was found under the declared metadata. "
                "This is not proof that an arbitrary pipeline is leakage-free."
            ),
        }


def audit_records(records: Iterable[TemporalRecord], cutoff: str | datetime, *, require_availability: bool = True) -> AuditReport:
    c = parse_ts(cutoff)
    if c is None:
        raise ValueError("cutoff is required")
    findings: list[AuditFinding] = []
    seen: set[str] = set()
    count = 0
    for r in records:
        count += 1
        if r.id in seen:
            findings.append(AuditFinding("DUPLICATE_ID", r.id, "error", "duplicate record id"))
        seen.add(r.id)
        if r.observed_at > c:
            findings.append(AuditFinding("FUTURE_OBSERVATION", r.id, "error", "observation timestamp is after cutoff"))
        if r.available_at is None:
            if require_availability:
                findings.append(AuditFinding("MISSING_AVAILABILITY", r.id, "warning", "availability timestamp is missing"))
        elif r.available_at > c:
            findings.append(AuditFinding("POST_CUTOFF_AVAILABILITY", r.id, "error", "information was not available by cutoff"))
        if r.label_available_at is not None and r.label_available_at > c:
            findings.append(AuditFinding("IMMATURE_LABEL", r.id, "error", "label outcome matures after cutoff"))
        if r.revised_at is not None and r.revised_at > c and r.available_at is not None and r.available_at <= c:
            findings.append(AuditFinding("POST_CUTOFF_REVISION", r.id, "warning", "record has a later revision; historical vintage may differ"))
    status = "fail" if any(f.severity == "error" for f in findings) else ("review" if findings else "pass")
    return AuditReport(c, status, tuple(findings), count)
