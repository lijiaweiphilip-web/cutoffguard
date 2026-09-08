"""Conformance audit for a small, explicit temporal run manifest.

The manifest checks declarations made by a researcher. It does not trace an
opaque feature pipeline or prove that the declaration matches every runtime
operation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import AuditFinding, AuditReport
from .contracts import FindingCategory, Severity
from .errors import InputFormatError, SchemaError
from .io import load_csv, load_jsonl
from .records import TemporalRecord, parse_ts

_MANIFEST_CODES = {
    "TRAIN_RECORD_AFTER_CUTOFF",
    "TRAIN_INFORMATION_NOT_AVAILABLE",
    "TRAIN_LABEL_NOT_MATURE",
    "SPLIT_ID_OVERLAP",
    "UNKNOWN_RECORD_ID",
    "ARTIFACT_BUILT_AFTER_CUTOFF",
    "ARTIFACT_FIT_AFTER_CUTOFF",
    "ARTIFACT_USES_EVAL_SPLIT",
    "INVALID_CUTOFF_ORDER",
    "MISSING_SPLIT",
    "EMPTY_TRAIN_SPLIT",
    "MANIFEST_PATH_ESCAPE",
}


def _manifest_finding(
    code: str,
    record_id: str,
    message: str,
    *,
    field: str | None = None,
    observed: Any = None,
    expected: Any = None,
) -> AuditFinding:
    category = FindingCategory.INPUT.value
    if code.startswith("TRAIN_"):
        category = FindingCategory.AVAILABILITY.value
    elif code.startswith("ARTIFACT_"):
        category = FindingCategory.ARTIFACT.value
    elif code.startswith(("SPLIT_", "UNKNOWN_")) or code in {
        "MISSING_SPLIT",
        "EMPTY_TRAIN_SPLIT",
    }:
        category = FindingCategory.SPLIT.value
    return AuditFinding(
        code,
        record_id,
        Severity.ERROR.value,
        message,
        category,
        field,
        observed,
        expected,
    )


def _finish(cutoff, findings: list[AuditFinding], count: int) -> AuditReport:
    findings.sort(key=lambda f: (f.code, f.record_id, f.field or ""))
    counts: dict[str, int] = {}
    for item in findings:
        counts[item.code] = counts.get(item.code, 0) + 1
    status = "fail" if findings else "pass"
    return AuditReport(
        cutoff,
        status,
        tuple(findings),
        count,
        schema_version="1.0",
        finding_counts=counts,
        assurance_boundary=(
            "This is a conformance audit of declared record/split/artifact metadata. "
            "It does not trace undocumented runtime behavior or prove arbitrary-pipeline safety."
        ),
    )


def _safe_external_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or candidate.drive or ".." in candidate.parts:
        raise InputFormatError(
            f"MANIFEST_PATH_ESCAPE: records path must stay inside {base}"
        )
    resolved_base = base.resolve()
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError as exc:
        raise InputFormatError(
            "MANIFEST_PATH_ESCAPE: records path escapes manifest directory"
        ) from exc
    if not resolved.exists():
        raise InputFormatError(f"records file does not exist: {value}")
    return resolved


def _records_from_manifest(
    manifest: dict[str, Any], source: Path
) -> list[TemporalRecord]:
    records = manifest["records"]
    if isinstance(records, list):
        out: list[TemporalRecord] = []
        for index, item in enumerate(records):
            try:
                out.append(TemporalRecord.from_dict(item))
            except (InputFormatError, ValueError) as exc:
                raise SchemaError(f"records[{index}]: {exc}") from exc
        return out
    path = _safe_external_path(source.parent, records)
    if path.suffix.lower() == ".jsonl":
        return load_jsonl(path)
    if path.suffix.lower() == ".csv":
        return load_csv(path)
    raise InputFormatError("records path must have .jsonl or .csv extension")


def load_manifest(path: str | Path) -> tuple[dict[str, Any], Path]:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputFormatError(
            f"cannot read manifest {source}: {exc.strerror or exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise SchemaError(
            f"{source}: invalid JSON at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(data, dict):
        raise SchemaError("manifest must be a JSON object")
    required = {
        "schema_version",
        "run_id",
        "training_cutoff",
        "evaluation_cutoff",
        "records",
        "splits",
        "artifacts",
    }
    unknown = sorted(set(data) - required - {"notes"})
    missing = sorted(required - set(data))
    if unknown:
        raise SchemaError(f"manifest: unknown keys: {', '.join(unknown)}")
    if missing:
        raise SchemaError(f"manifest: missing keys: {', '.join(missing)}")
    if data.get("schema_version") != "1.0":
        raise SchemaError("manifest: schema_version must be '1.0'")
    if not isinstance(data.get("run_id"), str) or not data["run_id"].strip():
        raise SchemaError("manifest.run_id must be a non-empty string")
    if not isinstance(data.get("splits"), list) or not isinstance(
        data.get("artifacts"), list
    ):
        raise SchemaError("manifest.splits and manifest.artifacts must be arrays")
    return data, source


def audit_manifest(path: str | Path) -> AuditReport:
    manifest, source = load_manifest(path)
    try:
        train_cutoff = parse_ts(manifest["training_cutoff"])
        eval_cutoff = parse_ts(manifest["evaluation_cutoff"])
    except (InputFormatError, ValueError) as exc:
        raise SchemaError(f"manifest cutoff: {exc}") from exc
    if train_cutoff is None or eval_cutoff is None:
        raise SchemaError("manifest cutoffs are required")
    findings: list[AuditFinding] = []
    if train_cutoff > eval_cutoff:
        findings.append(
            _manifest_finding(
                "INVALID_CUTOFF_ORDER",
                manifest["run_id"],
                "training_cutoff must not be after evaluation_cutoff",
                field="training_cutoff",
                observed=train_cutoff.isoformat(),
                expected=eval_cutoff.isoformat(),
            )
        )
    records = _records_from_manifest(manifest, source)
    by_id = {r.id: r for r in records}
    splits = manifest["splits"]
    split_map: dict[str, list[str]] = {}
    for index, split in enumerate(splits):
        if not isinstance(split, dict) or set(split) != {"name", "record_ids"}:
            raise SchemaError(
                f"manifest.splits[{index}] must contain only name and record_ids"
            )
        name = split.get("name")
        ids = split.get("record_ids")
        if not isinstance(name, str) or not name:
            raise SchemaError(f"manifest.splits[{index}].name must be non-empty")
        if name in split_map:
            findings.append(
                _manifest_finding(
                    "SPLIT_ID_OVERLAP",
                    name,
                    "split name is duplicated",
                    field=f"splits[{index}].name",
                )
            )
        if not isinstance(ids, list) or any(
            not isinstance(item, str) or not item for item in ids
        ):
            raise SchemaError(
                f"manifest.splits[{index}].record_ids must be an array of non-empty strings"
            )
        split_map[name] = ids
    for required_split in ("train", "validation", "test"):
        if required_split not in split_map:
            findings.append(
                _manifest_finding(
                    "MISSING_SPLIT",
                    required_split,
                    f"required split {required_split!r} is missing",
                )
            )
    if not split_map.get("train"):
        findings.append(
            _manifest_finding(
                "EMPTY_TRAIN_SPLIT",
                "train",
                "train split must contain at least one record",
            )
        )
    seen_split_ids: dict[str, str] = {}
    for split_name, ids in split_map.items():
        for record_id in ids:
            previous = seen_split_ids.get(record_id)
            if previous is not None:
                location = (
                    "the same split"
                    if previous == split_name
                    else f"both {previous!r} and {split_name!r}"
                )
                findings.append(
                    _manifest_finding(
                        "SPLIT_ID_OVERLAP", record_id, f"record id occurs in {location}"
                    )
                )
            seen_split_ids[record_id] = split_name
            if record_id not in by_id:
                findings.append(
                    _manifest_finding(
                        "UNKNOWN_RECORD_ID",
                        record_id,
                        f"split {split_name!r} references an unknown record",
                    )
                )
    train_ids = split_map.get("train", [])
    for record_id in train_ids:
        record = by_id.get(record_id)
        if record is None:
            continue
        if record.observed_at > train_cutoff:
            findings.append(
                _manifest_finding(
                    "TRAIN_RECORD_AFTER_CUTOFF",
                    record_id,
                    "training record is observed after training cutoff",
                    field="observed_at",
                    observed=record.observed_at.isoformat(),
                    expected=train_cutoff.isoformat(),
                )
            )
        if record.available_at is None or record.available_at > train_cutoff:
            findings.append(
                _manifest_finding(
                    "TRAIN_INFORMATION_NOT_AVAILABLE",
                    record_id,
                    "training information is not declared available by training cutoff",
                    field="available_at",
                    observed=record.available_at.isoformat()
                    if record.available_at
                    else None,
                    expected=train_cutoff.isoformat(),
                )
            )
        if (
            record.label_available_at is not None
            and record.label_available_at > train_cutoff
        ):
            findings.append(
                _manifest_finding(
                    "TRAIN_LABEL_NOT_MATURE",
                    record_id,
                    "training label is not mature by training cutoff",
                    field="label_available_at",
                    observed=record.label_available_at.isoformat(),
                    expected=train_cutoff.isoformat(),
                )
            )
    eval_names = {"validation", "test"}
    for index, artifact in enumerate(manifest["artifacts"]):
        if not isinstance(artifact, dict):
            raise SchemaError(f"manifest.artifacts[{index}] must be an object")
        required_artifact = {"id", "kind", "built_at", "fit_until", "source_splits"}
        unknown = sorted(set(artifact) - required_artifact)
        missing = sorted(required_artifact - set(artifact))
        if unknown or missing:
            raise SchemaError(
                f"manifest.artifacts[{index}] keys invalid; missing={missing}, unknown={unknown}"
            )
        artifact_id = artifact["id"]
        try:
            built_at = parse_ts(artifact["built_at"])
            fit_until = parse_ts(artifact["fit_until"])
        except (InputFormatError, ValueError) as exc:
            raise SchemaError(f"manifest.artifacts[{index}] timestamp: {exc}") from exc
        source_splits = artifact["source_splits"]
        if not isinstance(source_splits, list) or any(
            not isinstance(item, str) or not item for item in source_splits
        ):
            raise SchemaError(
                f"manifest.artifacts[{index}].source_splits must be an array of strings"
            )
        if built_at is not None and built_at > train_cutoff:
            findings.append(
                _manifest_finding(
                    "ARTIFACT_BUILT_AFTER_CUTOFF",
                    artifact_id,
                    "artifact was built after training cutoff",
                    field="built_at",
                    observed=built_at.isoformat(),
                    expected=train_cutoff.isoformat(),
                )
            )
        if fit_until is not None and fit_until > train_cutoff:
            findings.append(
                _manifest_finding(
                    "ARTIFACT_FIT_AFTER_CUTOFF",
                    artifact_id,
                    "artifact fit window extends after training cutoff",
                    field="fit_until",
                    observed=fit_until.isoformat(),
                    expected=train_cutoff.isoformat(),
                )
            )
        bad_splits = sorted(eval_names.intersection(source_splits))
        if bad_splits:
            findings.append(
                _manifest_finding(
                    "ARTIFACT_USES_EVAL_SPLIT",
                    artifact_id,
                    f"artifact declares evaluation split use: {', '.join(bad_splits)}",
                    field="source_splits",
                    observed=bad_splits,
                    expected=["train"],
                )
            )
    return _finish(eval_cutoff, findings, len(records))


def manifest_template() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "run_id": "replace-with-run-id",
        "training_cutoff": "2024-01-01T00:00:00Z",
        "evaluation_cutoff": "2024-06-01T00:00:00Z",
        "records": "records.jsonl",
        "splits": [
            {"name": "train", "record_ids": []},
            {"name": "validation", "record_ids": []},
            {"name": "test", "record_ids": []},
        ],
        "artifacts": [],
        "notes": {},
    }


def write_manifest_template(output_dir: str | Path) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "run-manifest.json"
    target.write_text(
        json.dumps(manifest_template(), indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return target
