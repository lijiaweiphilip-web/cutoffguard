"""Single source of truth for public finding explanations."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .contracts import FindingCategory, FindingCode, Severity


@dataclass(frozen=True)
class FindingDefinition:
    code: str
    category: str
    default_severity: str
    short_explanation: str
    remediation: str
    applies_to: str


_DEFINITIONS = (
    FindingDefinition(
        FindingCode.EMPTY_INPUT.value,
        FindingCategory.INPUT.value,
        Severity.WARNING.value,
        "No records were provided for audit.",
        "Provide at least one declared record or explain why the input is empty.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.DUPLICATE_ID.value,
        FindingCategory.IDENTITY.value,
        Severity.ERROR.value,
        "A record identifier occurs more than once.",
        "Make record identifiers unique before auditing.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.FUTURE_OBSERVATION.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "An observation timestamp is after the selected cutoff.",
        "Remove or re-scope records that were not observed by the cutoff.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.MISSING_AVAILABILITY.value,
        FindingCategory.AVAILABILITY.value,
        Severity.WARNING.value,
        "A record has no declared availability timestamp.",
        "Declare when the information became available, or explicitly allow missing values.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.POST_CUTOFF_AVAILABILITY.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "Information was not declared available by the selected cutoff.",
        "Use a historical vintage available by the cutoff.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.IMMATURE_LABEL.value,
        FindingCategory.LABEL_MATURITY.value,
        Severity.ERROR.value,
        "The label outcome matures after the selected cutoff.",
        "Keep label maturity within the declared evaluation horizon.",
        "record audit",
    ),
    FindingDefinition(
        FindingCode.POST_CUTOFF_REVISION.value,
        FindingCategory.REVISION.value,
        Severity.WARNING.value,
        "A later revision may differ from the historical vintage.",
        "Record the vintage used or re-run with the information available at the cutoff.",
        "record audit",
    ),
)

FINDING_REGISTRY = {item.code: item for item in _DEFINITIONS}


def list_definitions() -> tuple[FindingDefinition, ...]:
    return tuple(FINDING_REGISTRY[code] for code in sorted(FINDING_REGISTRY))


def explain(code: str) -> FindingDefinition | None:
    return FINDING_REGISTRY.get(code)


def definitions_as_dict() -> list[dict[str, str]]:
    return [asdict(item) for item in list_definitions()]
