from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from .audit import AuditReport


def render_json(report: AuditReport) -> str:
    return (
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=False)
        + "\n"
    )


def render_html(report: AuditReport) -> str:
    rows = (
        "".join(
            f"<tr><td><code>{html.escape(f.code)}</code></td><td>{html.escape(f.record_id)}</td><td>{html.escape(f.severity)}</td><td>{html.escape(f.message)}</td></tr>"
            for f in report.findings
        )
        or '<tr><td colspan="4">No listed finding.</td></tr>'
    )
    status_class = {"pass": "ok", "review": "warn", "fail": "bad"}[report.status]
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CutoffGuard report</title>
<style>body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:980px;margin:40px auto;padding:0 20px;color:#172033}}h1{{margin-bottom:4px}}.card{{border:1px solid #d9deea;border-radius:14px;padding:20px;margin:18px 0;box-shadow:0 2px 10px #0000000b}}.pill{{display:inline-block;padding:4px 10px;border-radius:999px;font-weight:700}}.ok{{background:#dcfce7;color:#166534}}.warn{{background:#fef3c7;color:#92400e}}.bad{{background:#fee2e2;color:#991b1b}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border-bottom:1px solid #e5e7eb;padding:9px;vertical-align:top}}code{{background:#f3f4f6;padding:2px 5px;border-radius:5px}}small{{color:#667085}}@media(max-width:640px){{body{{margin:18px auto}}table{{font-size:13px}}}}</style></head><body>
<h1>CutoffGuard</h1><div><span class="pill {status_class}">{report.status.upper()}</span></div>
<div class="card"><b>Cutoff</b>: {html.escape(report.cutoff.isoformat())}<br><b>Checked records</b>: {report.checked_records}</div>
<div class="card"><h2>Findings</h2><table><thead><tr><th>Code</th><th>Record</th><th>Severity</th><th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="card"><h2>Assurance boundary</h2><p>Findings are limited to the declared metadata and implemented checks. The report does not establish that arbitrary hidden pipeline behavior is leakage-free.</p></div>
<small>Generated locally by CutoffGuard.</small></body></html>"""


def render_sarif(report: AuditReport) -> str:
    """Render a deterministic SARIF 2.1.0 result for code-scanning tools."""
    rules: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    for finding in report.findings:
        rules.setdefault(
            finding.code,
            {
                "id": finding.code,
                "shortDescription": {"text": finding.code.replace("_", " ").title()},
                "help": {"text": finding.message},
            },
        )
        result: dict[str, object] = {
            "ruleId": finding.code,
            "level": "error" if finding.severity == "error" else "warning",
            "message": {"text": finding.message},
            "properties": {
                "category": finding.category,
                "record_id": finding.record_id,
            },
        }
        if finding.field:
            result["properties"]["field"] = finding.field  # type: ignore[index]
        if finding.observed is not None:
            result["properties"]["observed"] = finding.observed  # type: ignore[index]
        if finding.expected is not None:
            result["properties"]["expected"] = finding.expected  # type: ignore[index]
        if finding.evidence is not None:
            result["properties"]["evidence"] = finding.evidence  # type: ignore[index]
        results.append(result)
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "CutoffGuard",
                        "version": report.tool_version,
                        "informationUri": "https://github.com/lijiaweiphilip-web/cutoffguard",
                        "rules": [rules[key] for key in sorted(rules)],
                    }
                },
                "results": results,
                "properties": {
                    "cutoffguard_status": report.status,
                    "checked_records": report.checked_records,
                    "assurance_boundary": report.assurance_boundary,
                },
            }
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def render_junit(report: AuditReport) -> str:
    """Render findings as a small standards-compatible JUnit test suite."""
    suite = ET.Element(
        "testsuite",
        {
            "name": "cutoffguard",
            "tests": str(max(1, len(report.findings))),
            "failures": str(sum(f.severity == "error" for f in report.findings)),
            "skipped": str(sum(f.severity != "error" for f in report.findings)),
        },
    )
    if not report.findings:
        ET.SubElement(suite, "testcase", {"name": "temporal_conformance"})
    else:
        for finding in report.findings:
            case = ET.SubElement(
                suite,
                "testcase",
                {"name": f"{finding.code}:{finding.record_id}"},
            )
            detail = finding.message
            if finding.field:
                detail = f"{detail} (field={finding.field})"
            if finding.severity == "error":
                ET.SubElement(case, "failure", {"message": detail}).text = detail
            else:
                ET.SubElement(case, "skipped", {"message": detail})
    ET.SubElement(suite, "system-out").text = (
        f"status={report.status}; checked_records={report.checked_records}; "
        "assurance_boundary=" + report.assurance_boundary
    )
    return ET.tostring(suite, encoding="unicode") + "\n"


def render_report(report: AuditReport, fmt: str) -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "html":
        return render_html(report)
    if fmt == "sarif":
        return render_sarif(report)
    if fmt == "junit":
        return render_junit(report)
    raise ValueError(f"unsupported report format: {fmt}")


def write_report(report: AuditReport, path: str | Path, fmt: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        render_report(report, fmt),
        encoding="utf-8",
        newline="\n",
    )
