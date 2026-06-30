# AI Transparency Notice

**Effective date**: 2026-06-30
**Regulation**: EU Artificial Intelligence Act (EU 2024/1689)

---

## What AI systems are used here

This repository uses **GitHub Copilot** (a General Purpose AI model, Art. 3(63) EU AI Act)
to assist in generating Dagster ingest asset code via the workflow described in
`.github/copilot-instructions.md`.

GitHub Copilot is provided by Microsoft and is subject to its own GPAI obligations
under Art. 53–56 of the EU AI Act. Microsoft's compliance documentation is available
at [aka.ms/ai-transparency](https://aka.ms/ai-transparency).

---

## Risk classification (Art. 6 + Annex III)

This system is classified as **Limited Risk** under the EU AI Act.

It does not fall within Annex III high-risk categories (not critical infrastructure,
not employment decision-making, not law enforcement, not education assessment).

---

## Applicable transparency obligations

| Article | Obligation | How we comply |
|---------|-----------|---------------|
| Art. 50(1) | Inform users interacting with AI systems | PR template discloses AI use per contribution |
| Art. 52(1) | Label AI-generated content | `# EU AI Act Art. 52` header in every Copilot-generated file |
| Art. 53(1)(b) | GPAI deployer transparency to downstream users | This notice + per-PR disclosure |

---

## What AI generates and what humans review

| AI generates | Human must verify |
|-------------|-------------------|
| Asset function body (fetch/replicate logic) | Correctness of API/query logic |
| File and function names | Naming follows `.github/copilot-instructions.md` |
| Decorator and metadata patterns | Correct group, resource keys, output contract |
| Registration in `defs_sandbox.py` | `dagster asset list` passes; CI is green |

AI does **not** make merge decisions. No PR is merged without explicit human approval.

---

## Human oversight contact

For concerns about AI-generated contributions in this repository, open a GitHub issue
tagged `eu-ai-act` or contact the repository owner via GitHub.

---

## Record retention

AI contribution records are appended to `compliance/audit_log/contributions.jsonl`
(gitignored locally; maintainers are responsible for copying to durable storage for
the retention period required by their organisation's compliance programme).
