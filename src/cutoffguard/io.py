from __future__ import annotations

import csv
import json
from pathlib import Path

from .records import TemporalRecord


def load_jsonl(path: str | Path) -> list[TemporalRecord]:
    out=[]
    for lineno,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: obj=json.loads(line)
        except json.JSONDecodeError as e: raise ValueError(f"invalid JSON on line {lineno}: {e}") from e
        out.append(TemporalRecord.from_dict(obj))
    return out


def load_csv(path: str | Path) -> list[TemporalRecord]:
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return [TemporalRecord.from_dict(row) for row in csv.DictReader(f)]
