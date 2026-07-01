# Changelog

## 0.1.2 — 2026-07-01

- Fix: logo nodes use ASCII `o` instead of `○` (double-width in Rich SVG, causing misalignment)
- Fix: remove downloads badge (pypistats.org indexes new packages with a 24h delay)

## 0.1.1 — 2026-07-01

- Fix: screenshots now display correctly on PyPI (converted to PNG with absolute URLs)

## 0.1.0 — 2026-07-01

Initial release.

- `pr-agent scaffold` CLI — generate EU AI Act-compliant ingest files for REST, GraphQL, and DB replication
- `BaseRestFetcher`, `BaseGraphQLFetcher`, `PaginatedGraphQLFetcher`, `BaseDbReplicator` — framework-agnostic base classes
- Optional Dagster integration: `BaseRestAsset`, `BaseGraphQLAsset`, `BaseDbReplicationAsset`
- `DevEnvSecretResolver` — reads `PR_AGENT__<GROUP>__<KEY>` env vars; swappable for AWS SSM etc.
- `log_ai_contribution()` — local JSONL audit trail for EU AI Act Art. 52 compliance
- `.github/` workflows: CI (unit tests, Dagster integration, CLI smoke test), EU AI Act Art. 50 disclosure check, PyPI trusted publishing
- `compliance/` — AI transparency notice (Art. 52/53) and human oversight policy (Art. 14)
