# pr-automation-agent

A production-ready scaffold and shared library for automating ingest PRs with GitHub
Copilot. Works with **plain Python, Prefect, Airflow, or Dagster** — no specific
pipeline framework required. Built with **EU AI Act compliance** (Art. 50, 52, 53)
from day one, as of the June 2026 version of the Act.

## What you get

| Component | Description |
|-----------|-------------|
| `pr-agent scaffold` CLI | Generate a correctly structured ingest file in seconds |
| `BaseRestFetcher`, `BaseGraphQLFetcher`, `BaseDbReplicator` | Implement one method, get file I/O and output paths for free |
| `DevEnvSecretResolver` + `AbstractSecretResolver` | Env-var resolver for dev/CI; swap for AWS SSM, GCP Secret Manager, etc. in production |
| Dagster integration layer | Optional `BaseRestAsset`, `BaseGraphQLAsset`, `BaseDbReplicationAsset` for Dagster users |
| `log_ai_contribution()` | Append EU AI Act audit records after AI-generated PRs are merged |
| `.github/` workflows | CI that runs unit tests, materializes examples, and enforces EU AI Act disclosure |
| `compliance/` | AI transparency notice (Art. 52/53) and human oversight policy (Art. 14) |

---

## Install

```bash
# Plain Python / any framework (no pipeline deps)
pip install pr-automation-agent

# With Dagster integration
pip install "pr-automation-agent[dagster]"
```

---

## Quickstart: scaffold your first ingest file

```bash
# REST ingest (plain Python, works with any framework or none)
pr-agent scaffold rest --provider stripe --entity invoices

# GraphQL ingest
pr-agent scaffold graphql --provider github --entity issues

# DB replication
pr-agent scaffold db --engine postgres --table orders

# Preview without writing (--dry-run works with any type)
pr-agent scaffold rest --provider stripe --entity invoices --dry-run
```

Each command writes a ready-to-use file with the correct name, base class,
output path, and EU AI Act header. Fill in the TODOs and call it from
your pipeline, cron job, or script.

### Dagster variant

If your repo uses Dagster, add `--framework dagster` to get an `@asset`-decorated file:

```bash
pr-agent scaffold rest --provider stripe --entity invoices --framework dagster
pr-agent scaffold db   --engine postgres --table orders    --framework dagster
```

---

## Base classes in 5 lines

```python
from pr_automation_agent import BaseRestFetcher

class StripeInvoices(BaseRestFetcher):
    provider = "stripe"
    entity = "invoices"

    def fetch_all(self) -> list[dict]:
        import requests
        r = requests.get(
            "https://api.stripe.com/v1/invoices",
            headers={"Authorization": f"Bearer {os.environ['STRIPE_KEY']}"},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["data"]

# Call from anywhere — a cron job, a Prefect flow, a plain script
path, rows = StripeInvoices().run()
print(f"Wrote {rows} rows to {path}")
```

---

## Dagster: wire up Definitions

If your repo uses Dagster, import from the Dagster integration layer:

```python
from pr_automation_agent.integrations.dagster import BaseRestAsset, dev_env_secret_resolver_resource
from dagster import Definitions, load_assets_from_modules

import myrepo.ingest.rest.stripe.invoices_asset as stripe_invoices

defs = Definitions(
    assets=load_assets_from_modules([stripe_invoices]),
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
```

---

## Run the examples

```bash
# Plain Python (no extras needed)
python examples/plain/rest/jsonplaceholder/posts_fetch.py
python examples/plain/graphql/countries/countries_fetch.py

# Dagster (requires [dagster] extra)
dagster asset list -m examples.dagster.defs
dagster asset materialize --select fetch_jsonplaceholder_posts -m examples.dagster.defs
dagster asset materialize --select fetch_countries_countries   -m examples.dagster.defs

# DB example (requires env vars)
export PR_AGENT__POSTGRES__URI="sqlite:///demo.db"
export PR_AGENT__POSTGRES__SINCE="1970-01-01"
python examples/plain/db/postgres/orders_replicate.py
```

---

## Run tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## EU AI Act compliance summary

Risk classification: **Limited Risk** (not Annex III high-risk).

| Article | Obligation | Implementation |
|---------|-----------|----------------|
| Art. 50 | Disclose AI interaction | PR template checkbox + `ai-generated` label |
| Art. 52 | Label AI-generated content | Art. 52 header in every generated file |
| Art. 53/56 | GPAI deployer transparency | `compliance/AI_TRANSPARENCY_NOTICE.md` |
| Art. 14 (practice) | Human oversight | `compliance/HUMAN_OVERSIGHT_POLICY.md` + required review |

See [`compliance/`](compliance/) for full documentation.

---

## Connecting other repos

See [CONNECTING.md](CONNECTING.md) — GitHub template path and pip-install path,
including how to plug in production secret backends.

## License

Apache 2.0
