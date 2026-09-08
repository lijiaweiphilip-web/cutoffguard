# Report formats

The CLI emits deterministic JSON by default. HTML is intended for a local
human-readable preview; SARIF 2.1.0 is suitable for code-scanning ingestion;
JUnit XML is suitable for test-report ingestion.

```bash
cutoffguard audit-manifest examples/run-manifest/clean/run.json \
  --format sarif --output results/manifest.sarif
cutoffguard audit-manifest examples/run-manifest/clean/run.json \
  --format junit --output results/manifest.xml
```

SARIF and JUnit describe the findings produced by the declared-input audit.
They do not imply that GitHub uploaded, reviewed, or accepted a report unless a
workflow explicitly does so.
