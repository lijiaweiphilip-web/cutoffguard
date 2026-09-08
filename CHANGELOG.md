# Changelog

## 0.2.0 (candidate)

### Added

- Typed audit contracts and stable finding categories/codes.
- Run Manifest v1 for declared temporal cutoffs, split membership, and
  preprocessing artifact boundaries.
- Packaged JSON Schemas and a schema synchronization check.
- SARIF 2.1.0 and JUnit XML report formats alongside JSON and HTML.

### Changed

- Input errors now have stable exit code `4` and line-aware remediation
  messages; `--debug` is opt-in for tracebacks.
- Findings and reports carry structured metadata and deterministic ordering.
- The public examples state the conformance-audit boundary explicitly.

### Compatibility

- Existing `TemporalRecord`, `audit_records`, JSON/HTML output, and finding
  codes remain available.

### Known limitations

- A declaration-level audit cannot observe opaque runtime feature engineering,
  vendor transformations, network access, or arbitrary model code.

## 0.1.0

- Initial cutoff-aware record audit.
- Availability, label-maturity, revision, duplicate-ID checks.
- Future-perturbation diagnostic.
- JSON/HTML reports, CLI, deterministic fixtures, tests, and packaging.
- Required `observed_at` input validation with a regression test.
- CI quality gates for Ruff, mypy, build metadata, and twine; the controlled
  demo's expected failure exit code is asserted explicitly.
