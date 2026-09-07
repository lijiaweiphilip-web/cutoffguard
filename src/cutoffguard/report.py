from __future__ import annotations

import html
import json
from pathlib import Path

from .audit import AuditReport


def render_json(report: AuditReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


def render_html(report: AuditReport) -> str:
    rows = "".join(
        f"<tr><td><code>{html.escape(f.code)}</code></td><td>{html.escape(f.record_id)}</td><td>{html.escape(f.severity)}</td><td>{html.escape(f.message)}</td></tr>"
        for f in report.findings
    ) or '<tr><td colspan="4">No listed finding.</td></tr>'
    status_class = {"pass":"ok", "review":"warn", "fail":"bad"}[report.status]
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CutoffGuard report</title>
<style>body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:980px;margin:40px auto;padding:0 20px;color:#172033}}h1{{margin-bottom:4px}}.card{{border:1px solid #d9deea;border-radius:14px;padding:20px;margin:18px 0;box-shadow:0 2px 10px #0000000b}}.pill{{display:inline-block;padding:4px 10px;border-radius:999px;font-weight:700}}.ok{{background:#dcfce7;color:#166534}}.warn{{background:#fef3c7;color:#92400e}}.bad{{background:#fee2e2;color:#991b1b}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border-bottom:1px solid #e5e7eb;padding:9px;vertical-align:top}}code{{background:#f3f4f6;padding:2px 5px;border-radius:5px}}small{{color:#667085}}@media(max-width:640px){{body{{margin:18px auto}}table{{font-size:13px}}}}</style></head><body>
<h1>CutoffGuard</h1><div><span class="pill {status_class}">{report.status.upper()}</span></div>
<div class="card"><b>Cutoff</b>: {html.escape(report.cutoff.isoformat())}<br><b>Checked records</b>: {report.checked_records}</div>
<div class="card"><h2>Findings</h2><table><thead><tr><th>Code</th><th>Record</th><th>Severity</th><th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="card"><h2>Assurance boundary</h2><p>No listed temporal violation was found only means the declared metadata passed the implemented checks. It is not a proof that an arbitrary model, feature pipeline, vendor dataset, or opaque training process is leakage-free.</p></div>
<small>Generated locally by CutoffGuard.</small></body></html>'''


def write_report(report: AuditReport, path: str | Path, fmt: str) -> None:
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_json(report) if fmt=="json" else render_html(report), encoding="utf-8")
