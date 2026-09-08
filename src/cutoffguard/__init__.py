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
from .finding_registry import FINDING_REGISTRY, FindingDefinition
from .perturb import PerturbationResult, future_perturbation_test
from .records import TemporalRecord

__all__ = [
    "AuditConfigurationError",
    "AuditFinding",
    "AuditReport",
    "AuditStatus",
    "CutoffGuardError",
    "FINDING_REGISTRY",
    "FindingDefinition",
    "FindingCategory",
    "FindingCode",
    "InputFormatError",
    "PerturbationResult",
    "SchemaError",
    "Severity",
    "TemporalRecord",
    "__version__",
    "audit_records",
    "future_perturbation_test",
]
