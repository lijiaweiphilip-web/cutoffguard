from __future__ import annotations

import argparse
from pathlib import Path

from .audit import audit_records
from .demo import run_demo
from .io import load_csv, load_jsonl
from .report import render_json, write_report


def parser():
    p=argparse.ArgumentParser(prog="cutoffguard", description="Audit declared temporal availability in ML/research pipelines.")
    p.add_argument("--version", action="version", version="cutoffguard 0.1.0")
    sub=p.add_subparsers(dest="cmd", required=True)
    a=sub.add_parser("audit", help="audit CSV/JSONL temporal records")
    a.add_argument("input")
    a.add_argument("--cutoff", required=True)
    a.add_argument("--format", choices=["json","html"], default="json")
    a.add_argument("--output")
    a.add_argument("--allow-missing-availability", action="store_true")
    d=sub.add_parser("demo", help="run the packaged controlled demo")
    d.add_argument("--format", choices=["json","html"], default="json")
    d.add_argument("--output")
    return p


def main(argv=None):
    args=parser().parse_args(argv)
    if args.cmd=="demo":
        report=run_demo()
    else:
        path=Path(args.input)
        records=load_jsonl(path) if path.suffix.lower()==".jsonl" else load_csv(path)
        report=audit_records(records,args.cutoff,require_availability=not args.allow_missing_availability)
    if args.output:
        write_report(report,args.output,args.format)
    else:
        if args.format=="json": print(render_json(report))
        else:
            from .report import render_html
            print(render_html(report))
    return 2 if report.status=="fail" else (1 if report.status=="review" else 0)

if __name__=="__main__": raise SystemExit(main())
