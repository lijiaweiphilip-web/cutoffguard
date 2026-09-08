from __future__ import annotations

import csv
import json
from pathlib import Path

from .errors import InputFormatError
from .records import TemporalRecord


def load_jsonl(path: str | Path) -> list[TemporalRecord]:
    source = Path(path)
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InputFormatError(f"cannot read {source}: {exc.strerror or exc}") from exc
    out: list[TemporalRecord] = []
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputFormatError(
                f"{source}:{lineno}: invalid JSON: {exc.msg}"
            ) from exc
        try:
            out.append(TemporalRecord.from_dict(obj))
        except (InputFormatError, ValueError) as exc:
            raise InputFormatError(f"{source}:{lineno}: {exc}") from exc
    return out


def load_csv(path: str | Path) -> list[TemporalRecord]:
    source = Path(path)
    try:
        with source.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                if source.stat().st_size == 0:
                    return []
                raise InputFormatError(f"{source}: missing CSV header")
            required = {"id", "observed_at"}
            missing = sorted(required.difference(reader.fieldnames))
            if missing:
                raise InputFormatError(
                    f"{source}: missing CSV header fields: {', '.join(missing)}"
                )
            out: list[TemporalRecord] = []
            for lineno, row in enumerate(reader, 2):
                try:
                    out.append(TemporalRecord.from_dict(row))
                except (InputFormatError, ValueError) as exc:
                    raise InputFormatError(f"{source}:{lineno}: {exc}") from exc
            return out
    except InputFormatError:
        raise
    except OSError as exc:
        raise InputFormatError(f"cannot read {source}: {exc.strerror or exc}") from exc
