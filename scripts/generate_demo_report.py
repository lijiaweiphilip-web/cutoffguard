from pathlib import Path

from cutoffguard.demo import run_demo
from cutoffguard.report import write_report

root = Path(__file__).resolve().parents[1]
write_report(run_demo(), root / "results" / "demo_report.html", "html")
write_report(run_demo(), root / "results" / "demo_report.json", "json")
print(root / "results" / "demo_report.html")
