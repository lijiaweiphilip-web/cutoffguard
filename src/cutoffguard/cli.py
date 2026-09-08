from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from .audit import audit_records
from .demo import run_demo
from .errors import CutoffGuardError
from .io import load_csv, load_jsonl
from .report import render_json, write_report
from . import __version__


def parser():
    p = argparse.ArgumentParser(
        prog="cutoffguard",
        description="Audit declared temporal availability in ML/research pipelines.",
    )
    p.add_argument("--version", action="version", version=f"cutoffguard {__version__}")
    p.add_argument(
        "--debug",
        action="store_true",
        help="show a traceback for an expected input error",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="audit CSV/JSONL temporal records")
    a.add_argument("input")
    a.add_argument("--cutoff", required=True)
    a.add_argument("--format", choices=["json", "html"], default="json")
    a.add_argument("--output")
    a.add_argument("--allow-missing-availability", action="store_true")
    a.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    d = sub.add_parser("demo", help="run the packaged controlled demo")
    d.add_argument("--format", choices=["json", "html"], default="json")
    d.add_argument("--output")
    d.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.cmd == "demo":
            report = run_demo()
        else:
            path = Path(args.input)
            if path.suffix.lower() == ".jsonl":
                records = load_jsonl(path)
            elif path.suffix.lower() == ".csv":
                records = load_csv(path)
            else:
                raise CutoffGuardError("unsupported input format; use .jsonl or .csv")
            report = audit_records(
                records,
                args.cutoff,
                require_availability=not args.allow_missing_availability,
            )
        if args.output:
            write_report(report, args.output, args.format)
        elif args.format == "json":
            print(render_json(report), end="")
        else:
            from .report import render_html

            print(render_html(report))
        return 2 if report.status == "fail" else (1 if report.status == "review" else 0)
    except Exception as exc:
        if getattr(args, "debug", False):
            traceback.print_exc()
        else:
            print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 4)


if __name__ == "__main__":
    raise SystemExit(main())
