# CI integration

The repository workflow runs the test, formatting, typing, report, coverage,
and built-artifact smoke checks on Ubuntu and Windows. The matrix covers
Python 3.10 through 3.13 and uses `fail-fast: false` so a failure does not
hide another platform result.

The optional composite action in `action.yml` installs the checked-out source,
runs `audit-manifest`, and writes SARIF/JUnit files. It does not upload reports,
publish data, or grant permissions beyond the calling workflow.

For a local quality gate:

```bash
pytest --cov=cutoffguard --cov-report=term-missing --cov-fail-under=95
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m mypy src
python -m build
python -m twine check dist/*
python scripts/package_smoke.py dist
```
