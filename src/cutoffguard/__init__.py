"""CutoffGuard public API."""

from ._version import __version__

from .audit import AuditFinding, AuditReport, audit_records
from .contracts import AuditStatus, FindingCategory, FindingCode, Severity
from .errors import (
    AuditConfigurationError,
    CutoffGuardError,
    InputFormatError,
    SchemaError,
)
from .manifest import audit_manifest, load_manifest, manifest_template
from .perturb import PerturbationResult, future_perturbation_test
from .records import TemporalRecord

__all__ = [
    "AuditFinding",
    "AuditReport",
    "AuditStatus",
    "AuditConfigurationError",
    "CutoffGuardError",
    "FindingCategory",
    "FindingCode",
    "InputFormatError",
    "audit_manifest",
    "load_manifest",
    "manifest_template",
    "PerturbationResult",
    "SchemaError",
    "Severity",
    "TemporalRecord",
    "audit_records",
    "future_perturbation_test",
    "__version__",
]
