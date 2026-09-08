# CutoffGuard

[![CI](https://github.com/lijiaweiphilip-web/cutoffguard/actions/workflows/ci.yml/badge.svg)](https://github.com/lijiaweiphilip-web/cutoffguard/actions/workflows/ci.yml)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Cutoff-aware leakage diagnostics for time-series ML, research pipelines, and model validation.**

This branch prepares the v0.2.0 release; the latest published release remains
v0.1.0. The release line is still under review; this repository is
not published to PyPI.

Temporal leakage is often subtler than overlapping train/test rows. An observation can describe the past while becoming available only later; a forward target can mature after the declared training cutoff; a revised historical series can differ from the vintage actually available; and preprocessing can accidentally depend on future values.

CutoffGuard makes those boundaries explicit and testable.

## What it checks

- observations timestamped after a declared cutoff;
- information whose declared `available_at` is after the cutoff;
- labels that mature after the cutoff;
- later revisions that deserve vintage review;
- missing availability metadata rather than silently treating it as clean;
- future-dependence through a deterministic **future-perturbation test**.

## Quick start

```bash
python -m pip install -e .
cutoffguard demo --format html --output results/demo_report.html
cutoffguard audit examples/clean.jsonl --cutoff 2024-03-05T00:00:00Z
cutoffguard audit examples/contaminated.jsonl --cutoff 2024-04-15T00:00:00Z
cutoffguard audit-manifest examples/run-manifest/clean/run.json
```

Exit codes are `0=pass`, `1=review`, `2=fail`, and `4=invalid input or
configuration`. Use `--format sarif` or `--format junit` to write reports for
code-scanning or test-report tooling.

The controlled `demo` intentionally includes a contaminated example, so it
writes a report and returns exit code `2`; this is expected for the demo.

## Minimal record

```json
{"id":"gdp_q1","observed_at":"2024-03-31T00:00:00Z","available_at":"2024-04-25T12:30:00Z","source":"release_calendar"}
```

Auditing it at `2024-04-15T00:00:00Z` reports `POST_CUTOFF_AVAILABILITY`: the row describes Q1, but the declared information was not yet available.

## Future perturbation

```python
from cutoffguard import future_perturbation_test

def expanding_mean(values, cutoff):
    return [sum(values[:i+1])/(i+1) for i in range(cutoff+1)]

result = future_perturbation_test([1,2,3,4,5], 2, expanding_mean)
print(result.stable)
```

If changing only post-cutoff values changes a pre-cutoff output, inspect the pipeline for future dependence. If it does **not** change, that is evidence for this particular invariance test, not a mathematical certificate of zero leakage.

## Run Manifest v1

For an experiment with explicit train/validation/test membership, use
`cutoffguard audit-manifest run.json`. The manifest audit checks declared
cutoff ordering, record availability and label maturity, split identity, and
artifact build/fit boundaries. Records can be inline or a safe relative CSV or
JSONL path. `cutoffguard schema manifest` prints the packaged JSON Schema.

The manifest is a declaration-level conformance check. It cannot observe
undocumented runtime feature engineering, vendor transformations, model
weights, network access, or hidden filesystem behavior. A clean report is not
a general zero-leakage certificate. See
[`docs/RUN_MANIFEST.md`](docs/RUN_MANIFEST.md) for the complete boundary.

The same report can be emitted as JSON, HTML, SARIF 2.1.0, or JUnit XML:

```bash
cutoffguard audit-manifest examples/run-manifest/clean/run.json --format sarif --output results/manifest.sarif
cutoffguard audit-manifest examples/run-manifest/clean/run.json --format junit --output results/manifest.xml
```

Packaged schemas are loaded with `importlib.resources`, so the schema commands
also work after installing a wheel or source distribution. Root `schemas/`
copies are synchronized from `src/cutoffguard/schemas/` by
`python scripts/sync_schemas.py` and checked for byte equality in CI.

## Research-engineering boundary

CutoffGuard is deliberately narrow. It checks declared time/provenance metadata and controlled invariances. It cannot observe undocumented vendor transformations, opaque model weights, or arbitrary hidden feature-generation code. A clean report therefore means **no implemented failure was demonstrated under the provided record**, not “the project is guaranteed leakage-free.”

## Why this repository exists

This project turns temporal-validation practices into an installable, inspectable research tool. It complements task-specific empirical work by making the validation contract reusable across forecasting, financial ML, macroeconomic studies, and other time-ordered experiments.

See [`docs/QUICKSTART.md`](docs/QUICKSTART.md), [`docs/CONCEPTS.md`](docs/CONCEPTS.md),
[`docs/RUN_MANIFEST.md`](docs/RUN_MANIFEST.md), [`docs/REPORT_FORMATS.md`](docs/REPORT_FORMATS.md),
[`docs/SCHEMA.md`](docs/SCHEMA.md), and [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Development

```bash
python -m pip install -e .[dev]
pytest
python scripts/generate_demo_report.py
python -m build
python -m twine check dist/*
python scripts/package_smoke.py dist
```

## License

MIT. See [LICENSE](LICENSE).
