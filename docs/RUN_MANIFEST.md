# Run Manifest v1

`cutoffguard audit-manifest` checks a small declaration of the temporal
boundaries used by a run. A manifest points to records (or embeds them), names
train/validation/test split membership, and records when preprocessing
artifacts were built and fitted.

## What it can show

- a training record is not declared after the training cutoff;
- training information and labels are declared available by that cutoff;
- split IDs are unique and refer to known records;
- an artifact is not declared as fitted after the training cutoff or on an
  evaluation split; `built_at` is retained as provenance and is not itself a
  leakage decision;
- the training and evaluation cutoffs are ordered.

The check is deterministic and returns the same finding codes for the same
manifest and records. Validation and test records are checked against the
evaluation cutoff, including their declared availability and (when present)
label maturity. Artifact `fit_until` and `source_splits` drive the leakage
checks; an artifact may have been built later during a historical replay while
still fitting only data available by the declared cutoff.

## What it cannot show

This is a conformance audit of the declaration. A declared source split does
not prove that the runtime code used only that split. It cannot observe opaque
feature engineering, vendor transformations, model weights, or undocumented
network and filesystem behavior. A clean report is not a certificate of
arbitrary-pipeline leakage freedom.

## Example

```bash
cutoffguard audit-manifest examples/run-manifest/clean/run.json
```

The examples are synthetic and offline. Use `cutoffguard init manifest DIR` to
create an empty starting template for a real run; populate it from an auditable
experiment record rather than treating the template as evidence.
