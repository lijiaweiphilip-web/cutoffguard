"""Packaged JSON Schemas exposed without requiring a schema dependency."""

import json
from importlib.resources import files
from typing import Any

_SCHEMA_FILES = {
    "record": "record.schema.json",
    "report": "report.schema.json",
    "manifest": "run-manifest-v1.schema.json",
}


def schema_path(name: str):
    try:
        filename = _SCHEMA_FILES[name]
    except KeyError as exc:
        raise ValueError(
            f"unknown schema {name!r}; choose record, report, or manifest"
        ) from exc
    return files("cutoffguard").joinpath("schemas").joinpath(filename)


def load_schema(name: str) -> dict[str, Any]:
    return json.loads(schema_path(name).read_text(encoding="utf-8"))
