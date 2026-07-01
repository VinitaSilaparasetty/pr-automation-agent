# pr-automation-agent

**EU AI Act-compliant scaffold and shared library for automating ingest PRs with GitHub Copilot.**

Works with plain Python, Prefect, Airflow, Dagster, or any pipeline framework.
Zero pipeline framework required for the core package.

<img src="docs/assets/welcome.svg" alt="pr-agent welcome screen" width="700"/>

---

## Table of contents

- [What you get](#what-you-get)
- [Requirements](#requirements)
- [Install](#install)
- [Quickstart — plain Python](#quickstart--plain-python)
- [Quickstart — Dagster](#quickstart--dagster)
- [All scaffold options](#all-scaffold-options)
- [Secrets & configuration](#secrets--configuration)
- [EU AI Act compliance](#eu-ai-act-compliance)
- [Data & privacy (GDPR)](#data--privacy-gdpr)
- [Run the tests](#run-the-tests)
- [Connect your own repo](#connect-your-own-repo)
- [License](#license)

---

## What you get

| Component | Description |
|-----------|-------------|
| `pr-agent scaffold` CLI | Generate a correctly structured ingest file in seconds |
| `BaseRestFetcher` | Subclass and implement `fetch_all()` — REST ingest done |
| `BaseGraphQLFetcher` | Single-request GraphQL fetcher with cursor pagination variant |
| `BaseDbReplicator` | Incremental DB replication to Parquet with watermark support |
| `DevEnvSecretResolver` | Reads `PR_AGENT__<GROUP>__<KEY>` env vars — swap for AWS SSM etc. in prod |
| Dagster integration | Optional `BaseRestAsset`, `BaseGraphQLAsset`, `BaseDbReplicationAsset` |
| `log_ai_contribution()` | Append EU AI Act Art. 52 audit records locally after AI PRs merge |
| `.github/` workflows | CI that tests, materializes examples, enforces EU AI Act disclosure |
| `compliance/` | AI transparency notice (Art. 52/53) and human oversight policy (Art. 14) |

---

## Requirements

- Python 3.10 or higher
- pip or uv

No other dependencies for the core package. Dagster, pandas, sqlalchemy,
and requests are only needed if you use the Dagster integration or DB replication.

---

## Install

```bash
# Core only — plain Python / any framework (no pipeline deps)
pip install pr-automation-agent

# With Dagster integration + DB replication support
pip install "pr-automation-agent[dagster]"

# With uv
uv add pr-automation-agent
uv add "pr-automation-agent[dagster]"
```

**Startup time**: ~50 ms import, ~380 ms total CLI start. Dagster,
pandas, and sqlalchemy are lazy imports — they are never loaded unless
you explicitly call them. The CLI stays fast regardless of which extras
are installed.

Once installed, run `pr-agent` with no arguments to open the welcome screen.

---

## Quickstart — plain Python

No pipeline framework required. The generated file is a plain callable
you can import from any script, Prefect flow, Airflow task, cron job,
or Django management command.

**Step 1 — scaffold**

```bash
pr-agent scaffold rest --provider stripe --entity invoices
```

<img src="docs/assets/scaffold-rest.svg" alt="scaffold rest output" width="700"/>

This writes `rest/stripe/invoices_asset.py` (relative to your working directory)
and creates `__init__.py` in every new subdirectory automatically.

**Step 2 — fill in the TODOs**

Open the generated file and replace the placeholder URL and auth headers
with your real API call. Everything else — output path, date-stamped JSON,
row count — is handled by the base class.

**Step 3 — run it**

```bash
python rest/stripe/invoices_asset.py
# Wrote 120 rows to tmp/stripe/invoices/2026-07-01.json
```

Or import the function from your pipeline:

```python
from rest.stripe.invoices_asset import fetch_stripe_invoices

fetch_stripe_invoices()   # returns the output path
```

---

## Quickstart — Dagster

Only do this if your repo already uses Dagster. Add `--framework dagster`
to the scaffold command:

```bash
pr-agent scaffold rest --provider stripe --entity invoices --framework dagster
```

The generated file uses `BaseRestAsset` and the `@asset` decorator
instead of a plain callable. Register it in your `Definitions`:

```python
# defs.py
from dagster import Definitions, load_assets_from_modules
from pr_automation_agent.integrations.dagster import dev_env_secret_resolver_resource

import myrepo.ingest.rest.stripe.invoices_asset as stripe_invoices

defs = Definitions(
    assets=load_assets_from_modules([stripe_invoices]),
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
```

Verify it appears:

```bash
dagster asset list -m defs
```

---

## All scaffold options

```
pr-agent scaffold TYPE [OPTIONS]

TYPE:
  rest      REST API ingest
  graphql   GraphQL API ingest (single-request or cursor-paginated)
  db        Incremental DB replication to Parquet

OPTIONS (rest / graphql):
  --provider NAME    Provider name, e.g. stripe, github   [required]
  --entity NAME      Entity/resource name, e.g. invoices  [required]
  --framework NAME   dagster  (omit for plain Python)

OPTIONS (db):
  --engine NAME      DB engine, e.g. postgres, mysql       [required]
  --table NAME       Table to replicate                    [required]
  --framework NAME   dagster  (omit for plain Python)

SHARED:
  --output-dir PATH  Write into this directory (default: current dir)
  --dry-run          Print the file without writing it

EXAMPLES:
  pr-agent scaffold rest    --provider stripe  --entity invoices
  pr-agent scaffold graphql --provider github  --entity issues
  pr-agent scaffold db      --engine postgres  --table orders
  pr-agent scaffold db      --engine postgres  --table orders --dry-run
  pr-agent scaffold rest    --provider stripe  --entity invoices --framework dagster
```

<img src="docs/assets/scaffold-db.svg" alt="scaffold db output" width="700"/>

**Every generated file includes:**
- An EU AI Act Art. 52 header (date-stamped, names the tool)
- The correct base class import and subclass stub
- A single abstract method to implement (all I/O is handled for you)
- A `if __name__ == "__main__":` entry point (plain Python) or `@asset` decorator (Dagster)

---

## Secrets & configuration

The tool never touches your credentials directly. Set environment variables
before running:

```bash
# DB replication — postgres example
export PR_AGENT__POSTGRES__URI="postgresql://user:pass@localhost/mydb"
export PR_AGENT__POSTGRES__SINCE="2024-01-01"

# Any other secret group follows the same pattern:
# PR_AGENT__<GROUP>__<KEY>=<value>
```

`DevEnvSecretResolver` (the default) reads these at runtime. To use a
production secret backend, implement `AbstractSecretResolver`:

```python
from pr_automation_agent import AbstractSecretResolver, SecretReference

class AwsSsmSecretResolver(AbstractSecretResolver):
    def resolve_as_str(self, ref: SecretReference) -> str:
        import boto3
        return boto3.client("ssm").get_parameter(
            Name=f"/pr-agent/{ref.group_name}/{ref.key}",
            WithDecryption=True,
        )["Parameter"]["Value"]

# Pass at construction time (plain Python)
path, rows = PostgresOrders(AwsSsmSecretResolver()).run()
```

For Dagster, register it as a resource instead of `dev_env_secret_resolver_resource`.

---

## EU AI Act compliance

Risk classification: **Limited Risk** (not Annex III high-risk).

| Article | Obligation | What this package does |
|---------|-----------|------------------------|
| Art. 50 | Disclose AI interaction | PR template checkbox + `ai-generated` GitHub label |
| Art. 52 | Label AI-generated content | Header in every scaffolded file, auto-inserted |
| Art. 53/56 | GPAI deployer transparency | `compliance/AI_TRANSPARENCY_NOTICE.md` |
| Art. 14 (practice) | Human oversight | `compliance/HUMAN_OVERSIGHT_POLICY.md` + required PR review |

**Audit trail** — after a Copilot-generated PR is merged, record it:

```python
from pr_automation_agent import log_ai_contribution

log_ai_contribution(
    file_path="ingest/rest/stripe/invoices_asset.py",
    ai_model="GitHub Copilot",
    human_reviewer="@yourhandle",
    pr_number="123",
)
```

Records are appended to `compliance/audit_log/contributions.jsonl` —
a local file, never transmitted anywhere. See [`compliance/`](compliance/)
for the full policy documents.

---

## Data & privacy (GDPR)

**The tool does not collect, transmit, or store any personal data.**

| Question | Answer |
|----------|--------|
| Does it require an account or authentication? | No |
| Does it send data to Aevoxis or any third party? | No |
| Does it have telemetry or analytics? | No |
| Does it make network requests at startup or during scaffold? | No |
| Where are output files written? | Locally, to `tmp/` in your working directory |
| What does the audit log contain? | File path, AI model name, reviewer handle, PR number, timestamp — written locally only |
| Who controls the audit log? | You. It is a plain JSONL file in `compliance/audit_log/`. |

The `requests` library (used by `BaseRestFetcher` and `BaseGraphQLFetcher`) makes
HTTP calls **only to URLs you configure** in your own subclass — never
to Aevoxis or any default endpoint.

If your ingest files process personal data (e.g. user records from an API),
**you** are the data controller / processor under GDPR — the tool is
infrastructure, not a data processor itself.

For full GDPR and regulatory documentation see [`PRIVACY.md`](PRIVACY.md).

---

## Run the tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

31 tests covering resolvers, base classes, Dagster integration, and the
scaffold CLI (plain Python and Dagster variants, error cases, `--dry-run`,
`__init__.py` creation, provider sanitisation).

---

## Connect your own repo

See [CONNECTING.md](CONNECTING.md) for:

- **Path A — GitHub template**: click "Use this template", copy examples, done
- **Path B — pip install**: add to an existing repo in minutes
- Production secret backend examples (AWS SSM, GCP Secret Manager)

---

## License

GNU Affero General Public License v3 (AGPL-3.0).  
Copyright (C) 2025 Vinita Silaparasetty, Aevoxis Solutions.

For commercial use, enterprise deployment, or licensing enquiries:
**info@aevoxis.de** — [aevoxis.de](https://aevoxis.de)
