# CutoffGuard

[![CI](https://github.com/lijiaweiphilip-web/cutoffguard/actions/workflows/ci.yml/badge.svg)](https://github.com/lijiaweiphilip-web/cutoffguard/actions/workflows/ci.yml)
[![Python 3.10-3.12](https://img.shields.io/badge/python-3.10--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Cutoff-aware leakage diagnostics for time-series ML, research pipelines, and model validation.**

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
```

Exit codes are `0=pass`, `1=review`, `2=fail`.

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

## Research-engineering boundary

CutoffGuard is deliberately narrow. It checks declared time/provenance metadata and controlled invariances. It cannot observe undocumented vendor transformations, opaque model weights, or arbitrary hidden feature-generation code. A clean report therefore means **no implemented failure was demonstrated under the provided record**, not “the project is guaranteed leakage-free.”

## Why this repository exists

This project turns temporal-validation practices into an installable, inspectable research tool. It complements task-specific empirical work by making the validation contract reusable across forecasting, financial ML, macroeconomic studies, and other time-ordered experiments.

See [`docs/CONCEPTS.md`](docs/CONCEPTS.md), [`docs/SCHEMA.md`](docs/SCHEMA.md), and [`docs/FUTURE_PERTURBATION.md`](docs/FUTURE_PERTURBATION.md).

## Development

```bash
python -m pip install -e .[dev]
pytest
python scripts/generate_demo_report.py
python -m build
python -m twine check dist/*
```

## License

MIT. See [LICENSE](LICENSE).
