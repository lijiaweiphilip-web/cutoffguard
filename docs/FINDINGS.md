# Finding codes

This table is generated from `cutoffguard.finding_registry`; run `python scripts/generate_findings_doc.py` after changing a definition.

| Code | Category | Default severity | Meaning | Remediation | Applies to |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT_BUILT_AFTER_CUTOFF | artifact | error | An artifact build timestamp is later than the training cutoff. | Interpret built_at as provenance; use fit_until and source_splits for leakage checks. | run manifest (legacy diagnostic) |
| ARTIFACT_FIT_AFTER_CUTOFF | artifact | error | An artifact fit window extends after the training cutoff. | Keep fit_until within the declared training window. | run manifest |
| ARTIFACT_USES_EVAL_SPLIT | artifact | error | An artifact declares use of a validation or test split. | Fit the artifact from training data only. | run manifest |
| DUPLICATE_ARTIFACT_ID | artifact | error | An artifact identifier occurs more than once. | Give each artifact a unique identifier. | run manifest |
| DUPLICATE_ID | identity | error | A record identifier occurs more than once. | Make record identifiers unique before auditing. | record audit |
| EMPTY_INPUT | input | warning | No records were provided for audit. | Provide at least one declared record or explain why the input is empty. | record audit |
| EMPTY_TRAIN_SPLIT | split | error | The declared training split contains no records. | Provide at least one training record. | run manifest |
| EVALUATION_INFORMATION_NOT_AVAILABLE | availability | error | Validation or test information is not declared available by the evaluation cutoff. | Declare an availability timestamp within the evaluation window. | run manifest |
| EVALUATION_LABEL_NOT_MATURE | label_maturity | error | A validation or test label is not mature by the evaluation cutoff. | Declare label maturity within the evaluation window. | run manifest |
| EVALUATION_RECORD_AFTER_CUTOFF | availability | error | A validation or test record is observed after the evaluation cutoff. | Use records observed by the declared evaluation cutoff. | run manifest |
| FUTURE_OBSERVATION | availability | error | An observation timestamp is after the selected cutoff. | Remove or re-scope records that were not observed by the cutoff. | record audit |
| IMMATURE_LABEL | label_maturity | error | The label outcome matures after the selected cutoff. | Keep label maturity within the declared evaluation horizon. | record audit |
| INVALID_CUTOFF_ORDER | input | error | The training cutoff is later than the evaluation cutoff. | Declare cutoffs in chronological order. | run manifest |
| MANIFEST_PATH_ESCAPE | input | error | The records path escapes the manifest directory. | Use a safe relative records path inside the manifest bundle. | run manifest |
| MISSING_AVAILABILITY | availability | warning | A record has no declared availability timestamp. | Declare when the information became available, or explicitly allow missing values. | record audit |
| MISSING_SPLIT | split | error | A required train, validation, or test split is missing. | Declare all required split names. | run manifest |
| POST_CUTOFF_AVAILABILITY | availability | error | Information was not declared available by the selected cutoff. | Use a historical vintage available by the cutoff. | record audit |
| POST_CUTOFF_REVISION | revision | warning | A later revision may differ from the historical vintage. | Record the vintage used or re-run with the information available at the cutoff. | record audit |
| SPLIT_ID_OVERLAP | split | error | A record identifier occurs in more than one declared split. | Assign each record identifier to exactly one split. | run manifest |
| TRAIN_INFORMATION_NOT_AVAILABLE | availability | error | Training information is not declared available by the training cutoff. | Declare a historical availability timestamp within the training window. | run manifest |
| TRAIN_LABEL_NOT_MATURE | label_maturity | error | A training label is not mature by the training cutoff. | Use a label whose maturity is within the training window. | run manifest |
| TRAIN_RECORD_AFTER_CUTOFF | availability | error | A training record is observed after the training cutoff. | Use only records observed by the declared training cutoff. | run manifest |
| UNKNOWN_RECORD_ID | split | error | A split references a record identifier not present in the manifest records. | Add the record or remove the stale split reference. | run manifest |
| UNKNOWN_SOURCE_SPLIT | split | error | An artifact references a split not declared in the manifest. | Reference only declared split names. | run manifest |
