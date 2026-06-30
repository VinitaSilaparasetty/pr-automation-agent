# pr-automation-agent

A scaffold and shared library for automating Dagster ingest PRs with GitHub Copilot,
built with **EU AI Act compliance** from day one (Art. 50, 52, 53 — June 2026).

## What this repo provides

| Component | Description |
|-----------|-------------|
| `warehouse/` scaffold | Three runnable demo assets (REST, GraphQL, DB) that encode the exact file layout, naming, decorator, and output conventions Copilot needs |
| `src/pr_automation_agent/` | pip-installable package with `DevEnvSecretResolver` and `log_ai_contribution()` |
| `.github/copilot-instructions.md` | Agent authoring rules including mandatory EU AI Act Art. 52 file headers |
| `.github/PULL_REQUEST_TEMPLATE.md` | Per-PR AI disclosure form (Art. 50) |
| `.github/workflows/eu-ai-act-compliance.yml` | CI that enforces disclosure and Art. 52 headers |
| `compliance/` | System-level transparency notice and human oversight policy |

## Quick start

### 1. Use as a GitHub template

Click **"Use this template"** on GitHub, then adapt `warehouse/` paths and
`copilot-instructions.md` to your monorepo. See [CONNECTING.md](CONNECTING.md).

### 2. Install the package

```bash
pip install pr-automation-agent          # utilities only
pip install "pr-automation-agent[dagster]"  # + dagster, requests, pandas, pyarrow, sqlalchemy
```

### 3. Run the sandbox demos locally

```bash
pip install -e ".[dagster]"

# List assets
dagster asset list -m warehouse.oso_dagster.assets.ingest.defs_sandbox

# Materialize public demos (no secrets needed)
dagster asset materialize \
  --select fetch_jsonplaceholder_posts \
  -m warehouse.oso_dagster.assets.ingest.defs_sandbox

dagster asset materialize \
  --select fetch_countries_countries \
  -m warehouse.oso_dagster.assets.ingest.defs_sandbox

# DB demo (needs env vars)
export DAGSTER__POSTGRES__URI="sqlite:///demo.db"
export DAGSTER__POSTGRES__SINCE="1970-01-01"
dagster asset materialize \
  --select replicate_postgres_orders \
  -m warehouse.oso_dagster.assets.ingest.defs_sandbox
```

## Adding a new data source

1. Open a "New Ingest Asset" issue — the template gathers exactly what Copilot needs.
2. Copilot generates the asset following `.github/copilot-instructions.md`.
3. Open a PR; the EU AI Act compliance CI checks disclosure and Art. 52 headers.
4. A human reviewer verifies the output and approves.

## EU AI Act compliance summary

Risk classification: **Limited Risk** (not Annex III).

| Article | What | How |
|---------|------|-----|
| Art. 50 | Disclose AI interaction | PR template checkbox + `ai-generated` label |
| Art. 52 | Label AI-generated content | Header comment in every Copilot-generated file |
| Art. 53/56 | GPAI deployer transparency | `compliance/AI_TRANSPARENCY_NOTICE.md` |
| Art. 14 (practice) | Human oversight | `compliance/HUMAN_OVERSIGHT_POLICY.md` + required PR approval |

See [`compliance/`](compliance/) for full documentation.

## Connecting other repos

See [CONNECTING.md](CONNECTING.md) for the template-copy and pip-install integration paths.

## License

Apache 2.0
