from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from . import __version__
from .audit import audit_records
from .demo import run_demo
from .errors import CutoffGuardError
from .finding_registry import definitions_as_dict, explain, list_definitions
from .io import load_csv, load_jsonl
from .manifest import audit_manifest, write_manifest_template
from .report import render_report, write_report
from .schema import load_schema


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
    a.add_argument(
        "--format", choices=["json", "html", "sarif", "junit"], default="json"
    )
    a.add_argument("--output")
    a.add_argument("--allow-missing-availability", action="store_true")
    a.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    m = sub.add_parser("audit-manifest", help="audit a declared temporal run manifest")
    m.add_argument("manifest")
    m.add_argument(
        "--format", choices=["json", "html", "sarif", "junit"], default="json"
    )
    m.add_argument("--output")
    m.add_argument("--fail-on", choices=["review", "fail"], default="fail")
    m.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    d = sub.add_parser("demo", help="run the packaged controlled demo")
    d.add_argument(
        "--format", choices=["json", "html", "sarif", "junit"], default="json"
    )
    d.add_argument("--output")
    d.add_argument(
        "--debug",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    s = sub.add_parser("schema", help="print a packaged JSON schema")
    s.add_argument("name", choices=["record", "report", "manifest"])
    e = sub.add_parser("explain", help="explain a finding code")
    e.add_argument("code", nargs="?")
    e.add_argument("--list", action="store_true", help="list registered finding codes")
    e.add_argument("--format", choices=["text", "json"], default="text")
    i = sub.add_parser("init", help="create an empty template")
    i.add_argument("kind", choices=["manifest"])
    i.add_argument("output_dir")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.cmd == "schema":
            print(json.dumps(load_schema(args.name), indent=2) + "\n", end="")
            return 0
        if args.cmd == "explain":
            if args.list:
                if args.format == "json":
                    print(json.dumps(definitions_as_dict(), indent=2) + "\n", end="")
                else:
                    print("\n".join(item.code for item in list_definitions()))
                return 0
            if not args.code:
                raise CutoffGuardError("provide a finding code or use --list")
            definition = explain(args.code)
            if definition is None:
                raise CutoffGuardError(f"unknown finding code: {args.code}")
            if args.format == "json":
                print(json.dumps(definition.__dict__, indent=2) + "\n", end="")
            else:
                print(
                    f"{definition.code}: {definition.short_explanation}\n"
                    f"Category: {definition.category}\n"
                    f"Default severity: {definition.default_severity}\n"
                    f"Remediation: {definition.remediation}\n"
                    f"Applies to: {definition.applies_to}"
                )
            return 0
        if args.cmd == "init":
            target = write_manifest_template(args.output_dir)
            print(target)
            return 0
        if args.cmd == "demo":
            report = run_demo()
        elif args.cmd == "audit-manifest":
            report = audit_manifest(args.manifest)
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
        else:
            print(render_report(report, args.format), end="")
        if report.status == "fail":
            return 2
        if report.status == "review":
            return 2 if getattr(args, "fail_on", "fail") == "review" else 1
        return 0
    except (CutoffGuardError, OSError, ValueError, TypeError, KeyError) as exc:
        if getattr(args, "debug", False):
            traceback.print_exc()
        else:
            print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 4)


if __name__ == "__main__":
    raise SystemExit(main())
