# Connecting to pr-automation-agent

Two integration paths — use either or both.

---

## Path A: GitHub Template Repo

Use this if you want the `.github/` workflows, compliance files, and
`examples/` dropped into a new repository with one click.

1. On GitHub, click **"Use this template"** → **"Create a new repository"**.
2. Copy the `examples/plain/` assets you need into your own ingest directory.
3. Call `.run()` from whatever pipeline or script you use.
4. If you use Dagster, wire up `examples/dagster/defs.py` as a starting point.
5. Update `.github/copilot-instructions.md` with your provider/entity names.
6. Enable branch protection rules listed in `compliance/HUMAN_OVERSIGHT_POLICY.md`.

---

## Path B: pip install

Use this to add the base classes, scaffolder CLI, and secret resolver
utilities to an existing project.

```bash
# Plain Python / any framework
pip install pr-automation-agent

# With Dagster integration
pip install "pr-automation-agent[dagster]"
```

### Scaffold your first ingest file

```bash
# REST (plain Python — works with Prefect, Airflow, cron, or nothing)
pr-agent scaffold rest --provider stripe --entity invoices

# GraphQL
pr-agent scaffold graphql --provider github --entity issues

# DB replication
pr-agent scaffold db --engine postgres --table orders

# Dagster variant (if your repo uses Dagster)
pr-agent scaffold rest --provider stripe --entity invoices --framework dagster
```

Each command creates a correctly structured file with the EU AI Act Art. 52
header, the right base class wired up, and TODOs for only the parts that are
specific to your source.

### Call from your pipeline

The generated file exports a plain callable — import it from wherever your
pipeline expects it:

```python
# e.g. a Prefect flow, an Airflow task, or a cron script
from ingest.rest.stripe.invoices_asset import fetch_stripe_invoices

fetch_stripe_invoices()   # writes JSON to tmp/, returns the path
```

Or call `.run()` directly:

```python
from ingest.rest.stripe.invoices_asset import StripeInvoices

path, rows = StripeInvoices().run()
```

### Dagster: wire up Definitions

If your repo uses Dagster, scaffold with `--framework dagster` and wire up:

```python
# your_repo/defs.py
from dagster import Definitions, load_assets_from_modules
from pr_automation_agent.integrations.dagster import dev_env_secret_resolver_resource

import your_repo.ingest.rest.stripe.invoices_asset as stripe_invoices

defs = Definitions(
    assets=load_assets_from_modules([stripe_invoices]),
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
```

### Set secrets in dev/CI

`DevEnvSecretResolver` reads `PR_AGENT__<GROUP>__<KEY>` env vars:

```bash
export PR_AGENT__POSTGRES__URI="postgresql://user:pass@localhost/mydb"
export PR_AGENT__POSTGRES__SINCE="2024-01-01"
```

### Switch to a production secret backend

Implement `AbstractSecretResolver` against your secret store:

```python
from pr_automation_agent import AbstractSecretResolver, SecretReference

class AwsSsmSecretResolver(AbstractSecretResolver):
    def resolve_as_str(self, ref: SecretReference) -> str:
        import boto3
        client = boto3.client("ssm")
        param = client.get_parameter(
            Name=f"/pr-agent/{ref.group_name}/{ref.key}",
            WithDecryption=True,
        )
        return param["Parameter"]["Value"]
```

Pass it at construction time:

```python
path, rows = PostgresOrders(AwsSsmSecretResolver()).run()
```

Or in Dagster, register it as a resource instead of `dev_env_secret_resolver_resource`.

### Record AI contributions (EU AI Act audit trail)

After a Copilot-generated PR is merged:

```python
from pr_automation_agent import log_ai_contribution

log_ai_contribution(
    file_path="ingest/rest/stripe/invoices_asset.py",
    ai_model="GitHub Copilot",
    human_reviewer="@yourhandle",
    pr_number="123",
)
```

---

## Minimum EU AI Act setup for your fork

Copy these three files at minimum:

| File | EU AI Act obligation |
|------|---------------------|
| `.github/PULL_REQUEST_TEMPLATE.md` | Art. 50 — per-PR AI disclosure |
| `.github/workflows/eu-ai-act-compliance.yml` | Art. 50/52 — CI enforcement |
| `compliance/AI_TRANSPARENCY_NOTICE.md` | Art. 52/53 — system-level disclosure |

Update `AI_TRANSPARENCY_NOTICE.md` with your organisation name and contact.

---

## Questions / issues

Open a GitHub issue tagged `integration`.
