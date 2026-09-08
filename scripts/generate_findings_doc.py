"""Generate the public finding-code reference from the registry."""

from __future__ import annotations

import argparse
from pathlib import Path

from cutoffguard.finding_registry import list_definitions


def render() -> str:
    lines = [
        "# Finding codes",
        "",
        "This table is generated from `cutoffguard.finding_registry`; run `python scripts/generate_findings_doc.py` after changing a definition.",
        "",
        "| Code | Category | Default severity | Meaning | Remediation | Applies to |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in list_definitions():
        values = (
            item.code,
            item.category,
            item.default_severity,
            item.short_explanation,
            item.remediation,
            item.applies_to,
        )
        lines.append(
            "| " + " | ".join(value.replace("|", "\\|") for value in values) + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="fail if the checked-in file is stale"
    )
    args = parser.parse_args()
    target = Path(__file__).parents[1] / "docs" / "FINDINGS.md"
    expected = render()
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"{target} is stale; run generate_findings_doc.py")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8", newline="\n")
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
