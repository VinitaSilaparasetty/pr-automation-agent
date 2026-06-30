# pr-automation-agent

A production-ready scaffold and shared library for automating Dagster ingest PRs
with GitHub Copilot. Built with **EU AI Act compliance** (Art. 50, 52, 53) from
day one, as of the June 2026 version of the Act.

## What you get

| Component | Description |
|-----------|-------------|
| `pr-agent scaffold` CLI | Generate a correctly structured asset file in seconds |
| Base asset classes | `BaseRestAsset`, `BaseGraphQLAsset`, `PaginatedGraphQLAsset`, `BaseDbReplicationAsset` — implement one method, get file I/O and Dagster metadata for free |
| `DevEnvSecretResolver` + `AbstractSecretResolver` | Env-var resolver for dev/CI; swap for AWS SSM, GCP Secret Manager, etc. in production |
| `dev_env_secret_resolver_resource` | Drop-in Dagster resource — register in your `Definitions` |
| `log_ai_contribution()` | Append EU AI Act audit records after AI-generated PRs are merged |
| `.github/` workflows | CI that runs unit tests, materializes examples, and enforces EU AI Act disclosure |
| `compliance/` | AI transparency notice (Art. 52/53) and human oversight policy (Art. 14) |

---

## Install

```bash
pip install "pr-automation-agent[dagster]"
# or
uv add "pr-automation-agent[dagster]"
```

---

## Quickstart: scaffold your first asset

```bash
# REST ingest
pr-agent scaffold rest --provider stripe --entity invoices

# GraphQL ingest
pr-agent scaffold graphql --provider github --entity issues

# DB replication
pr-agent scaffold db --engine postgres --table orders
```

Each command writes a ready-to-use asset file with the correct name, decorator,
base class, output path, and EU AI Act header. Fill in the TODOs and register it.

### Preview (dry-run)

```bash
pr-agent scaffold rest --provider stripe --entity invoices --dry-run
```

---

## Wire up Definitions

```python
# defs.py
from dagster import Definitions, load_assets_from_modules
from pr_automation_agent import dev_env_secret_resolver_resource

import myrepo.ingest.rest.stripe.invoices_asset as stripe_invoices

defs = Definitions(
    assets=load_assets_from_modules([stripe_invoices]),
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
```

---

## Base classes in 5 lines

```python
from pr_automation_agent import BaseRestAsset

class StripeInvoices(BaseRestAsset):
    provider = "stripe"
    entity = "invoices"

    def fetch_all(self) -> list[dict]:
        import requests
        r = requests.get(
            "https://api.stripe.com/v1/invoices",
            headers={"Authorization": f"Bearer {self._token()}"},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["data"]
```

Then:

```python
@asset(group_name="rest_crawl")
def fetch_stripe_invoices(context: AssetExecutionContext) -> str:
    return StripeInvoices().materialize(context)
```

---

## Run the examples

```bash
# List all example assets
dagster asset list -m examples.defs

# Materialize (no auth needed)
dagster asset materialize --select fetch_jsonplaceholder_posts -m examples.defs
dagster asset materialize --select fetch_countries_countries -m examples.defs

# DB example (requires env vars)
export DAGSTER__POSTGRES__URI="sqlite:///demo.db"
export DAGSTER__POSTGRES__SINCE="1970-01-01"
dagster asset materialize --select replicate_postgres_orders -m examples.defs
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
