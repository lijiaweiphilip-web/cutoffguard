# Security

CutoffGuard reads local CSV/JSONL and manifest declarations and writes local
reports. It is not a sandbox for untrusted code and does not promise that
opaque feature pipelines, vendor transformations, or arbitrary model code are
leakage-free.

## Supported release

The latest supported release is shown on the public GitHub release page. The
`main` branch may contain unreleased changes; report a problem against the
version that actually ran.

## Reporting a security issue

Please use GitHub's private security advisory flow when possible:

<https://github.com/lijiaweiphilip-web/cutoffguard/security/advisories/new>

If that route is unavailable, open a minimal public issue without sensitive
details and request a private channel. Do not include passwords, API keys,
tokens, private paths, client records, or restricted datasets in issues,
fixtures, logs, or report attachments.

## Input-safety scope

Manifest paths are confined to the manifest directory and symlink escapes are
rejected. Treat reports and SARIF/JUnit files as potentially sensitive when
their input contains sensitive record identifiers. Finding messages are not a
guarantee that secrets cannot occur in user-supplied fields.
