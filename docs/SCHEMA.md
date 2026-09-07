# Record schema

| Field | Required | Meaning |
|---|---:|---|
| `id` | yes | stable record identifier |
| `observed_at` | yes | period/event timestamp, timezone-aware |
| `available_at` | recommended | first declared availability time |
| `label_available_at` | optional | maturity time for a future target |
| `revised_at` | optional | later revision marker |
| `value` | optional | value carried by the row |
| `source` | optional | human-readable source note |
