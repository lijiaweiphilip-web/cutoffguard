"""Stable string-valued contracts used by the public CutoffGuard API."""

from enum import Enum


class AuditStatus(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    FAIL = "fail"


class Severity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


class FindingCategory(str, Enum):
    AVAILABILITY = "availability"
    LABEL_MATURITY = "label_maturity"
    REVISION = "revision"
    IDENTITY = "identity"
    SPLIT = "split"
    ARTIFACT = "artifact"
    INPUT = "input"


class FindingCode(str, Enum):
    EMPTY_INPUT = "EMPTY_INPUT"
    DUPLICATE_ID = "DUPLICATE_ID"
    FUTURE_OBSERVATION = "FUTURE_OBSERVATION"
    MISSING_AVAILABILITY = "MISSING_AVAILABILITY"
    POST_CUTOFF_AVAILABILITY = "POST_CUTOFF_AVAILABILITY"
    IMMATURE_LABEL = "IMMATURE_LABEL"
    POST_CUTOFF_REVISION = "POST_CUTOFF_REVISION"
