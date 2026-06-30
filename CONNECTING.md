# Connecting to pr-automation-agent

Two integration paths — use either or both.

---

## Path A: GitHub Template Repo (scaffold copy)

Use this if you want the full folder structure, CI workflows, and compliance files
dropped into a new repository.

1. On GitHub, click **"Use this template"** → **"Create a new repository"**.
2. Adapt `warehouse/oso_dagster/` paths to match your monorepo layout.
3. Update `.github/copilot-instructions.md` with your provider/entity naming.
4. Enable branch protection rules listed in `compliance/HUMAN_OVERSIGHT_POLICY.md`.
5. Set your repo as a **template** (Settings → ✓ Template repository) so your
   downstream contributors can do the same.

---

## Path B: pip install (shared utilities only)

Use this if you already have a Dagster repo and only want the `DevEnvSecretResolver`
and audit logging utilities.

```bash
pip install pr-automation-agent
# or with uv:
uv add pr-automation-agent
```

Then in your `defs_sandbox.py`:

```python
from dagster import Definitions, load_assets_from_modules, resource
from pr_automation_agent import DevEnvSecretResolver, log_ai_contribution

@resource
def secret_resolver():
    return DevEnvSecretResolver()

# ... your asset modules ...
defs = Definitions(assets=assets, resources={"secret_resolver": secret_resolver})
```

And to record a merged AI contribution:

```python
from pr_automation_agent import log_ai_contribution

log_ai_contribution(
    file_path="warehouse/.../my_asset.py",
    ai_model="GitHub Copilot",
    human_reviewer="@yourhandle",
    pr_number="42",
)
```

---

## Minimum viable EU AI Act setup for your fork

Copy these three files at minimum:

| File | Purpose |
|------|---------|
| `.github/PULL_REQUEST_TEMPLATE.md` | Art. 50 disclosure on every PR |
| `.github/workflows/eu-ai-act-compliance.yml` | Enforces disclosure + Art. 52 headers |
| `compliance/AI_TRANSPARENCY_NOTICE.md` | System-level disclosure for your repo |

Then update `AI_TRANSPARENCY_NOTICE.md` with your organisation's name and contact.

---

## Questions / issues

Open a GitHub issue tagged `integration` in this repository.
