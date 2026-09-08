# Contributing

CutoffGuard is a small research-software project. Contributions should stay
bounded, reproducible, and explicit about what the implementation can observe.

## Development setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m mypy src
```

Run the public fixtures before opening a pull request:

```bash
cutoffguard audit examples/availability/clean.jsonl --cutoff 2024-04-15T00:00:00Z
cutoffguard audit-manifest examples/run-manifest/clean/run.json
```

## Change process

New finding codes need a failing test, a stable explanation, and an explicit
assurance boundary. Keep JSON, SARIF, JUnit, and HTML output deterministic for
the same input. Schema resources under `src/cutoffguard/schemas/` are the
source of truth; run `python scripts/sync_schemas.py` when the public root
copies need updating.

Pull requests should state the problem, scope, verification commands, and what
the change does not establish. Do not add private datasets, credentials,
client records, generated virtual environments, or local absolute paths to
fixtures or reports.

## Reporting a bug

Bug reports should include a minimal public record, declared cutoff, expected
finding, actual finding, operating system, Python version, and CutoffGuard
version. Remove credentials, private financial data, and restricted datasets
before attaching anything.
