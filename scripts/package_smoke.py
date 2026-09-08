"""Install both release artifact types outside the source tree and smoke-test them."""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path


def _run(python: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(python), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != expect:
        raise SystemExit(
            f"command failed ({result.returncode} != {expect}): {' '.join(args)}\n"
            f"stdout={result.stdout[-1000:]}\nstderr={result.stderr[-1000:]}"
        )
    return result


def _venv_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _project_version() -> str:
    """Read the version under test instead of freezing a staging version."""
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    with pyproject.open("rb") as stream:
        return str(tomllib.load(stream)["project"]["version"])


def _smoke(artifact: Path, label: str) -> None:
    with tempfile.TemporaryDirectory(prefix=f"cutoffguard-{label}-") as temp:
        env_root = Path(temp)
        _run(Path(sys.executable), "-m", "venv", str(env_root))
        python = _venv_python(env_root)
        if label == "sdist":
            # A source distribution is built in the clean venv, so provide the
            # wheel backend explicitly instead of relying on the source tree.
            _run(
                python,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "wheel",
            )
        _run(
            python,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            str(artifact),
        )
        version = _run(python, "-m", "cutoffguard.cli", "--version")
        expected_version = _project_version()
        if expected_version not in version.stdout:
            raise SystemExit(
                f"unexpected installed version from {label}: {version.stdout}"
                f" (expected {expected_version})"
            )
        schema = _run(python, "-m", "cutoffguard.cli", "schema", "manifest")
        if '"schema_version"' not in schema.stdout:
            raise SystemExit(f"packaged schema unavailable from {label}")
        _run(
            python,
            "-m",
            "cutoffguard.cli",
            "audit",
            str(
                Path(__file__).parents[1] / "examples" / "availability" / "clean.jsonl"
            ),
            "--cutoff",
            "2024-04-15T00:00:00Z",
        )
        clean_manifest = (
            Path(__file__).parents[1]
            / "examples"
            / "run-manifest"
            / "clean"
            / "run.json"
        )
        contaminated_manifest = (
            Path(__file__).parents[1]
            / "examples"
            / "run-manifest"
            / "split-overlap"
            / "run.json"
        )
        _run(python, "-m", "cutoffguard.cli", "audit-manifest", str(clean_manifest))
        for fmt, suffix in (("sarif", ".sarif"), ("junit", ".xml")):
            report = env_root / f"clean{suffix}"
            _run(
                python,
                "-m",
                "cutoffguard.cli",
                "audit-manifest",
                str(clean_manifest),
                "--format",
                fmt,
                "--output",
                str(report),
            )
            if fmt == "sarif":
                payload = json.loads(report.read_text(encoding="utf-8"))
                if payload.get("version") != "2.1.0":
                    raise SystemExit(f"invalid SARIF report from {label}")
            elif ET.parse(report).getroot().tag != "testsuite":
                raise SystemExit(f"invalid JUnit report from {label}")
        _run(
            python,
            "-m",
            "cutoffguard.cli",
            "audit-manifest",
            str(contaminated_manifest),
            expect=2,
        )


def main(argv: list[str] | None = None) -> int:
    dist = Path(argv[0] if argv else "dist").resolve()
    wheels = sorted(glob.glob(str(dist / "*.whl")))
    sdists = sorted(glob.glob(str(dist / "*.tar.gz")))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(f"expected one wheel and one sdist in {dist}")
    _smoke(Path(wheels[0]), "wheel")
    _smoke(Path(sdists[0]), "sdist")
    print("package smoke PASS: wheel and sdist installed outside source tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
