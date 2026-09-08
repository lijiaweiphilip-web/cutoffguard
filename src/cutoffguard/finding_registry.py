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
    FindingDefinition(
        FindingCode.TRAIN_RECORD_AFTER_CUTOFF.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "A training record is observed after the training cutoff.",
        "Use only records observed by the declared training cutoff.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.TRAIN_INFORMATION_NOT_AVAILABLE.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "Training information is not declared available by the training cutoff.",
        "Declare a historical availability timestamp within the training window.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.TRAIN_LABEL_NOT_MATURE.value,
        FindingCategory.LABEL_MATURITY.value,
        Severity.ERROR.value,
        "A training label is not mature by the training cutoff.",
        "Use a label whose maturity is within the training window.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.SPLIT_ID_OVERLAP.value,
        FindingCategory.SPLIT.value,
        Severity.ERROR.value,
        "A record identifier occurs in more than one declared split.",
        "Assign each record identifier to exactly one split.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.UNKNOWN_RECORD_ID.value,
        FindingCategory.SPLIT.value,
        Severity.ERROR.value,
        "A split references a record identifier not present in the manifest records.",
        "Add the record or remove the stale split reference.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.ARTIFACT_BUILT_AFTER_CUTOFF.value,
        FindingCategory.ARTIFACT.value,
        Severity.ERROR.value,
        "An artifact build timestamp is later than the training cutoff.",
        "Interpret built_at as provenance; use fit_until and source_splits for leakage checks.",
        "run manifest (legacy diagnostic)",
    ),
    FindingDefinition(
        FindingCode.ARTIFACT_FIT_AFTER_CUTOFF.value,
        FindingCategory.ARTIFACT.value,
        Severity.ERROR.value,
        "An artifact fit window extends after the training cutoff.",
        "Keep fit_until within the declared training window.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.ARTIFACT_USES_EVAL_SPLIT.value,
        FindingCategory.ARTIFACT.value,
        Severity.ERROR.value,
        "An artifact declares use of a validation or test split.",
        "Fit the artifact from training data only.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.INVALID_CUTOFF_ORDER.value,
        FindingCategory.INPUT.value,
        Severity.ERROR.value,
        "The training cutoff is later than the evaluation cutoff.",
        "Declare cutoffs in chronological order.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.MISSING_SPLIT.value,
        FindingCategory.SPLIT.value,
        Severity.ERROR.value,
        "A required train, validation, or test split is missing.",
        "Declare all required split names.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.EMPTY_TRAIN_SPLIT.value,
        FindingCategory.SPLIT.value,
        Severity.ERROR.value,
        "The declared training split contains no records.",
        "Provide at least one training record.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.MANIFEST_PATH_ESCAPE.value,
        FindingCategory.INPUT.value,
        Severity.ERROR.value,
        "The records path escapes the manifest directory.",
        "Use a safe relative records path inside the manifest bundle.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.EVALUATION_RECORD_AFTER_CUTOFF.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "A validation or test record is observed after the evaluation cutoff.",
        "Use records observed by the declared evaluation cutoff.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.EVALUATION_INFORMATION_NOT_AVAILABLE.value,
        FindingCategory.AVAILABILITY.value,
        Severity.ERROR.value,
        "Validation or test information is not declared available by the evaluation cutoff.",
        "Declare an availability timestamp within the evaluation window.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.EVALUATION_LABEL_NOT_MATURE.value,
        FindingCategory.LABEL_MATURITY.value,
        Severity.ERROR.value,
        "A validation or test label is not mature by the evaluation cutoff.",
        "Declare label maturity within the evaluation window.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.DUPLICATE_ARTIFACT_ID.value,
        FindingCategory.ARTIFACT.value,
        Severity.ERROR.value,
        "An artifact identifier occurs more than once.",
        "Give each artifact a unique identifier.",
        "run manifest",
    ),
    FindingDefinition(
        FindingCode.UNKNOWN_SOURCE_SPLIT.value,
        FindingCategory.SPLIT.value,
        Severity.ERROR.value,
        "An artifact references a split not declared in the manifest.",
        "Reference only declared split names.",
        "run manifest",
    ),
)

FINDING_REGISTRY = {item.code: item for item in _DEFINITIONS}


def list_definitions() -> tuple[FindingDefinition, ...]:
    return tuple(FINDING_REGISTRY[code] for code in sorted(FINDING_REGISTRY))


def explain(code: str) -> FindingDefinition | None:
    return FINDING_REGISTRY.get(code)


def definitions_as_dict() -> list[dict[str, str]]:
    return [asdict(item) for item in list_definitions()]
