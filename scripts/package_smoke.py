"""Install both release artifact types outside the source tree and smoke-test them."""

from __future__ import annotations

import glob
import os
from pathlib import Path
import subprocess
import sys
import tempfile


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
        if "0.2.0" not in version.stdout:
            raise SystemExit(
                f"unexpected installed version from {label}: {version.stdout}"
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
