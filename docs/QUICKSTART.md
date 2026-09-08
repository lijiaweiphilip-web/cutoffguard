# Quickstart

This walkthrough uses only the small synthetic fixtures shipped with the
repository. It is an offline engineering example, not a financial result.

```bash
python -m pip install -e .
cutoffguard --version
cutoffguard audit examples/availability/clean.jsonl --cutoff 2024-04-15T00:00:00Z
cutoffguard audit-manifest examples/run-manifest/clean/run.json
```

To inspect an intentional failure, run the contaminated fixture and review its
non-zero exit code:

```bash
cutoffguard audit examples/availability/contaminated.jsonl --cutoff 2024-04-15T00:00:00Z
```

For an installed wheel, use the wheel path rather than an editable install and
run `cutoffguard schema manifest` to verify the packaged schema resource.
