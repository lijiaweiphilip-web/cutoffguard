"""Validate the machine-readable reports produced by the composite action."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        raise SystemExit("usage: verify_reports.py SARIF_PATH JUNIT_PATH")
    sarif_path, junit_path = (Path(item) for item in args)
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    if sarif.get("version") != "2.1.0" or not sarif.get("runs"):
        raise SystemExit("invalid SARIF report")
    junit = ET.parse(junit_path).getroot()
    if junit.tag != "testsuite":
        raise SystemExit("invalid JUnit report")
    print("report validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
