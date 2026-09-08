from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from ._version import __version__
from .contracts import FindingCategory, FindingCode, Severity
from .errors import AuditConfigurationError
from .records import TemporalRecord, parse_ts


@dataclass(frozen=True)
class AuditFinding:
    code: str
    record_id: str
    severity: str
    message: str
    category: str = FindingCategory.INPUT.value
    field: str | None = None
    observed: Any = None
    expected: Any = None
    evidence: Any = None


@dataclass(frozen=True)
class AuditReport:
    cutoff: datetime
    status: str
    findings: tuple[AuditFinding, ...]
    checked_records: int
    schema_version: str = "1.0"
    tool_version: str = field(default_factory=lambda: __version__)
    finding_counts: dict[str, int] = field(default_factory=dict)
    assurance_boundary: str = (
        "Findings are limited to the declared metadata and implemented checks. "
        "The report does not establish that arbitrary hidden pipeline behavior "
        "is leakage-free."
    )
    generated_at: str | None = None

    def to_dict(self):
        result = {
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "cutoff": self.cutoff.isoformat(),
            "status": self.status,
            "checked_records": self.checked_records,
            "finding_counts": dict(sorted(self.finding_counts.items())),
            "findings": [asdict(f) for f in self.findings],
            "assurance_boundary": self.assurance_boundary,
        }
        if self.generated_at is not None:
            result["generated_at"] = self.generated_at
        return result


_SEVERITY_ORDER = {Severity.ERROR.value: 0, Severity.WARNING.value: 1}


def _finding(
    code: FindingCode,
    record_id: str,
    severity: Severity,
    message: str,
    category: FindingCategory,
    *,
    field: str | None = None,
    observed: Any = None,
    expected: Any = None,
    evidence: Any = None,
) -> AuditFinding:
    return AuditFinding(
        code.value,
        record_id,
        severity.value,
        message,
        category.value,
        field,
        observed,
        expected,
        evidence,
    )


def audit_records(
    records: Iterable[TemporalRecord],
    cutoff: str | datetime,
    *,
    require_availability: bool = True,
) -> AuditReport:
    c = parse_ts(cutoff)
    if c is None:
        raise AuditConfigurationError("cutoff is required")
    findings: list[AuditFinding] = []
    seen: set[str] = set()
    count = 0
    for r in records:
        count += 1
        if r.id in seen:
            findings.append(
                _finding(
                    FindingCode.DUPLICATE_ID,
                    r.id,
                    Severity.ERROR,
                    "duplicate record id",
                    FindingCategory.IDENTITY,
                )
            )
        seen.add(r.id)
        if r.observed_at > c:
            findings.append(
                _finding(
                    FindingCode.FUTURE_OBSERVATION,
                    r.id,
                    Severity.ERROR,
                    "observation timestamp is after cutoff",
                    FindingCategory.AVAILABILITY,
                    field="observed_at",
                    observed=r.observed_at.isoformat(),
                    expected=c.isoformat(),
                )
            )
        if r.available_at is None:
            if require_availability:
                findings.append(
                    _finding(
                        FindingCode.MISSING_AVAILABILITY,
                        r.id,
                        Severity.WARNING,
                        "availability timestamp is missing",
                        FindingCategory.AVAILABILITY,
                        field="available_at",
                        expected="timezone-aware timestamp",
                    )
                )
        elif r.available_at > c:
            findings.append(
                _finding(
                    FindingCode.POST_CUTOFF_AVAILABILITY,
                    r.id,
                    Severity.ERROR,
                    "information was not available by cutoff",
                    FindingCategory.AVAILABILITY,
                    field="available_at",
                    observed=r.available_at.isoformat(),
                    expected=c.isoformat(),
                )
            )
        if r.label_available_at is not None and r.label_available_at > c:
            findings.append(
                _finding(
                    FindingCode.IMMATURE_LABEL,
                    r.id,
                    Severity.ERROR,
                    "label outcome matures after cutoff",
                    FindingCategory.LABEL_MATURITY,
                    field="label_available_at",
                    observed=r.label_available_at.isoformat(),
                    expected=c.isoformat(),
                )
            )
        if (
            r.revised_at is not None
            and r.revised_at > c
            and r.available_at is not None
            and r.available_at <= c
        ):
            findings.append(
                _finding(
                    FindingCode.POST_CUTOFF_REVISION,
                    r.id,
                    Severity.WARNING,
                    "record has a later revision; historical vintage may differ",
                    FindingCategory.REVISION,
                    field="revised_at",
                    observed=r.revised_at.isoformat(),
                    expected=c.isoformat(),
                )
            )
    if count == 0:
        findings.append(
            _finding(
                FindingCode.EMPTY_INPUT,
                "",
                Severity.WARNING,
                "no records were provided for audit",
                FindingCategory.INPUT,
            )
        )
    findings.sort(
        key=lambda f: (
            _SEVERITY_ORDER.get(f.severity, 99),
            f.code,
            f.record_id,
            f.field or "",
        )
    )
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.code] = counts.get(finding.code, 0) + 1
    status = (
        "fail"
        if any(f.severity == Severity.ERROR.value for f in findings)
        else ("review" if findings else "pass")
    )
    return AuditReport(c, status, tuple(findings), count, finding_counts=counts)
