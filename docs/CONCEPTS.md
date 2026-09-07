# Concepts

CutoffGuard distinguishes four clocks that are frequently collapsed in temporal ML:

1. **Observation time** — what period an observation describes.
2. **Availability time** — when the value could actually have been consumed.
3. **Label-availability time** — when a forward-looking target has matured.
4. **Revision time** — when a later vintage may have changed the historical value.

A split based only on observation dates can still leak if availability or label maturity crosses the training cutoff.

## Assurance boundary

A `pass` is scoped to the provided metadata and implemented rules. It does not prove opaque feature-generation code, model weights, vendor histories, or unrecorded data flows are leakage-free.
