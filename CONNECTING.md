# Connecting to pr-automation-agent

Two integration paths — use either or both.

---

## Path A: GitHub Template Repo

Use this if you want the `.github/` workflows, compliance files, and
`examples/` dropped into a new repository with one click.

1. On GitHub, click **"Use this template"** → **"Create a new repository"**.
2. Copy the `examples/` assets you need into your own ingest directory.
3. Point your `Definitions` at your asset modules (see `examples/defs.py`).
4. Update `.github/copilot-instructions.md` with your provider/entity names.
5. Enable branch protection rules listed in `compliance/HUMAN_OVERSIGHT_POLICY.md`.

---

## Path B: pip install

Use this to add the base classes, scaffolder CLI, and secret resolver
utilities to an existing Dagster repo.

```bash
pip install "pr-automation-agent[dagster]"
# or with uv:
uv add "pr-automation-agent[dagster]"
```

### Scaffold your first asset

```bash
# REST
pr-agent scaffold rest --provider stripe --entity invoices

# GraphQL
pr-agent scaffold graphql --provider github --entity issues

# DB replication
pr-agent scaffold db --engine postgres --table orders
```

Each command creates a correctly structured asset file with the EU AI Act
Art. 52 header, the right base class wired up, and TODOs for only the
parts that are specific to your source.

### Wire up Definitions

```python
# your_repo/defs.py
from dagster import Definitions, load_assets_from_modules
from pr_automation_agent import dev_env_secret_resolver_resource

import your_repo.ingest.rest.stripe.invoices_asset as stripe_invoices
# ... other asset modules ...

defs = Definitions(
    assets=load_assets_from_modules([stripe_invoices, ...]),
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
```

### Switch to a production secret backend

`DevEnvSecretResolver` reads env vars. For production, implement
`AbstractSecretResolver` against your secret store:

```python
from pr_automation_agent import AbstractSecretResolver, SecretReference

class AwsSsmSecretResolver(AbstractSecretResolver):
    def resolve_as_str(self, ref: SecretReference) -> str:
        import boto3
        client = boto3.client("ssm")
        param = client.get_parameter(
            Name=f"/dagster/{ref.group_name}/{ref.key}",
            WithDecryption=True,
        )
        return param["Parameter"]["Value"]
```

Register it the same way:

```python
from dagster import resource

@resource
def aws_ssm_resolver():
    return AwsSsmSecretResolver()

defs = Definitions(assets=assets, resources={"secret_resolver": aws_ssm_resolver})
```

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
