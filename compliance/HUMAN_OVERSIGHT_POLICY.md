# Human Oversight Policy

**Applies to**: all AI-assisted pull requests in this repository
**Authority**: EU AI Act Art. 14 (good practice) and Art. 50 (transparency)

---

## Mandatory review steps for AI-generated PRs

Every PR that ticks "Yes — AI-assisted" or carries the `ai-generated` label **must**:

1. **Pass CI** — both `ingest-assets-ci` and `eu-ai-act-compliance` workflows must be green.
2. **Have at least one human approver** — the approver must not be the same account that
   opened the PR (including bot accounts).
3. **Include a reviewer comment** confirming they:
   - ran the asset locally or inspected CI artifact output
   - verified naming follows `.github/copilot-instructions.md`
   - confirmed the Art. 52 header is present in every generated file

## What reviewers must not do

- **Do not approve without running or inspecting outputs.** A green CI is necessary but not sufficient.
- **Do not enable auto-merge** for PRs labelled `ai-generated`.
- **Do not remove the `ai-generated` label** to bypass compliance checks.

## Escalation

If an AI-generated contribution causes a regression or produces incorrect data:

1. Revert the PR immediately.
2. Open an issue tagged `eu-ai-act` and `incident` describing what went wrong.
3. Record the incident in `compliance/audit_log/contributions.jsonl` with a `notes` field.
4. Review and tighten the Copilot instructions before re-attempting the contribution.

## Branch protection recommendations

Enable the following on `main`:
- Require status checks: `sandbox` (ingest-assets-ci), `disclosure-check` (eu-ai-act-compliance)
- Require at least 1 approving review
- Dismiss stale reviews on new push
- Do not allow bypassing the above settings for administrators
