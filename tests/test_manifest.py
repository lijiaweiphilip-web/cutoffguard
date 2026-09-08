import json
from pathlib import Path

import pytest

from cutoffguard.cli import main
from cutoffguard.errors import InputFormatError, SchemaError
from cutoffguard.manifest import audit_manifest, load_manifest, write_manifest_template
from cutoffguard.schema import load_schema


def write_case(tmp_path, *, records=None, splits=None, artifacts=None, **overrides):
    records = records or [
        {
            "id": "train_1",
            "observed_at": "2024-01-01T00:00:00Z",
            "available_at": "2024-01-02T00:00:00Z",
        },
        {
            "id": "val_1",
            "observed_at": "2024-02-01T00:00:00Z",
            "available_at": "2024-02-02T00:00:00Z",
        },
        {
            "id": "test_1",
            "observed_at": "2024-06-01T00:00:00Z",
            "available_at": "2024-06-02T00:00:00Z",
        },
    ]
    splits = splits or [
        {"name": "train", "record_ids": ["train_1"]},
        {"name": "validation", "record_ids": ["val_1"]},
        {"name": "test", "record_ids": ["test_1"]},
    ]
    data = {
        "schema_version": "1.0",
        "run_id": "case",
        "training_cutoff": "2024-01-31T00:00:00Z",
        "evaluation_cutoff": "2024-06-30T00:00:00Z",
        "records": "records.jsonl",
        "splits": splits,
        "artifacts": artifacts or [],
    }
    data.update(overrides)
    root = tmp_path / "manifest"
    root.mkdir()
    (root / "records.jsonl").write_text(
        "\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8"
    )
    path = root / "run.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def codes(report):
    return {item.code for item in report.findings}


def test_clean_manifest_passes(tmp_path):
    report = audit_manifest(write_case(tmp_path))
    assert report.status == "pass"
    assert report.checked_records == 3


@pytest.mark.parametrize(
    ("code", "change"),
    [
        (
            "TRAIN_RECORD_AFTER_CUTOFF",
            {
                "records": [
                    {
                        "id": "train_1",
                        "observed_at": "2024-02-01T00:00:00Z",
                        "available_at": "2024-02-02T00:00:00Z",
                    }
                ]
            },
        ),
        (
            "TRAIN_INFORMATION_NOT_AVAILABLE",
            {
                "records": [
                    {
                        "id": "train_1",
                        "observed_at": "2024-01-01T00:00:00Z",
                        "available_at": "2024-02-02T00:00:00Z",
                    }
                ]
            },
        ),
        (
            "TRAIN_LABEL_NOT_MATURE",
            {
                "records": [
                    {
                        "id": "train_1",
                        "observed_at": "2024-01-01T00:00:00Z",
                        "available_at": "2024-01-02T00:00:00Z",
                        "label_available_at": "2024-02-02T00:00:00Z",
                    }
                ]
            },
        ),
    ],
)
def test_train_boundary_findings(tmp_path, code, change):
    report = audit_manifest(
        write_case(
            tmp_path,
            records=change["records"]
            + [
                {
                    "id": "val_1",
                    "observed_at": "2024-02-01T00:00:00Z",
                    "available_at": "2024-02-02T00:00:00Z",
                },
                {
                    "id": "test_1",
                    "observed_at": "2024-06-01T00:00:00Z",
                    "available_at": "2024-06-02T00:00:00Z",
                },
            ],
        )
    )
    assert code in codes(report)


def test_split_overlap_and_unknown_id(tmp_path):
    report = audit_manifest(
        write_case(
            tmp_path,
            splits=[
                {"name": "train", "record_ids": ["train_1", "missing"]},
                {"name": "validation", "record_ids": ["train_1"]},
                {"name": "test", "record_ids": ["test_1"]},
            ],
        )
    )
    assert {"SPLIT_ID_OVERLAP", "UNKNOWN_RECORD_ID"} <= codes(report)


def test_artifact_checks(tmp_path):
    report = audit_manifest(
        write_case(
            tmp_path,
            artifacts=[
                {
                    "id": "scaler",
                    "kind": "preprocessor",
                    "built_at": "2024-02-01T00:00:00Z",
                    "fit_until": "2024-02-02T00:00:00Z",
                    "source_splits": ["train", "test"],
                }
            ],
        )
    )
    assert {
        "ARTIFACT_BUILT_AFTER_CUTOFF",
        "ARTIFACT_FIT_AFTER_CUTOFF",
        "ARTIFACT_USES_EVAL_SPLIT",
    } <= codes(report)


def test_missing_and_empty_splits(tmp_path):
    report = audit_manifest(
        write_case(tmp_path, splits=[{"name": "train", "record_ids": []}])
    )
    assert {"MISSING_SPLIT", "EMPTY_TRAIN_SPLIT"} <= codes(report)


def test_invalid_cutoff_order(tmp_path):
    report = audit_manifest(
        write_case(tmp_path, training_cutoff="2024-07-01T00:00:00Z")
    )
    assert "INVALID_CUTOFF_ORDER" in codes(report)


def test_inline_records_are_supported(tmp_path):
    path = write_case(tmp_path)
    data = json.loads(path.read_text())
    data["records"] = [
        {
            "id": "train_1",
            "observed_at": "2024-01-01T00:00:00Z",
            "available_at": "2024-01-02T00:00:00Z",
        },
        {
            "id": "val_1",
            "observed_at": "2024-02-01T00:00:00Z",
            "available_at": "2024-02-02T00:00:00Z",
        },
        {
            "id": "test_1",
            "observed_at": "2024-06-01T00:00:00Z",
            "available_at": "2024-06-02T00:00:00Z",
        },
    ]
    path.write_text(json.dumps(data))
    assert audit_manifest(path).status == "pass"


def test_path_escape_is_rejected(tmp_path):
    path = write_case(tmp_path)
    data = json.loads(path.read_text())
    data["records"] = "../outside.jsonl"
    path.write_text(json.dumps(data))
    with pytest.raises(InputFormatError, match="MANIFEST_PATH_ESCAPE"):
        audit_manifest(path)


def test_manifest_schema_and_template(tmp_path):
    schema = load_schema("manifest")
    assert schema["$schema"].endswith("draft/2020-12/schema")
    target = write_manifest_template(tmp_path)
    assert target.exists() and json.loads(target.read_text())["schema_version"] == "1.0"


def test_root_and_packaged_schemas_are_byte_identical():
    root = Path(__file__).parents[1] / "schemas"
    package = Path(__file__).parents[1] / "src" / "cutoffguard" / "schemas"
    for name in (
        "record.schema.json",
        "report.schema.json",
        "run-manifest-v1.schema.json",
    ):
        assert (root / name).read_bytes() == (package / name).read_bytes()


def test_schema_rejects_unknown_version(tmp_path):
    path = write_case(tmp_path)
    data = json.loads(path.read_text())
    data["schema_version"] = "2.0"
    path.write_text(json.dumps(data))
    with pytest.raises(SchemaError, match="schema_version"):
        load_manifest(path)


def test_cli_manifest_schema_explain_and_init(tmp_path, capsys):
    path = write_case(tmp_path)
    assert main(["audit-manifest", str(path)]) == 0
    assert '"status": "pass"' in capsys.readouterr().out
    assert main(["schema", "manifest"]) == 0
    assert '"schema_version"' in capsys.readouterr().out
    assert main(["explain", "POST_CUTOFF_AVAILABILITY"]) == 0
    assert "available" in capsys.readouterr().out
    assert main(["init", "manifest", str(tmp_path / "new")]) == 0
