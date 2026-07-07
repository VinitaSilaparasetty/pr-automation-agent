# pr-automation-agent

## What this repo is

A Python tool (`src/pr_automation_agent/`) that scaffolds EU AI Act Art. 52-compliant headers for AI-generated Python files. It was used as the reference implementation in the empirical paper below.

## The paper

`paper.md` is a full research paper targeting MSR / ICSE conference submission (≤10 pages body + ≤2 pages references, IEEE two-column format via `IEEEtran.cls`).

**Title:** "Measuring the Art. 52 Gap: A GitHub-Scale Empirical Study of EU AI Act Transparency Compliance in AI-Assisted Software Development"
**Author:** Vinita Silaparasetty, Aevoxis Solutions (info@aevoxis.de)
**Submission note:** at top of paper.md — convert to LaTeX for final submission.

### Paper structure

| Section | Content | Status |
|---|---|---|
| I | Introduction | Done |
| II | Background (incl. II.A jurisdictional scope) | Done |
| III | RQs and Hypotheses (H1–H3) | Done |
| IV | Methodology — E1 GitHub mining, E2 header survival, E3 PyPI audit, **IV.D Jurisdictional Scoping** | Done |
| V | Results — Tables I–IV, **V.D JS results (TABLE V & VI)** | Done |
| VI | Two blind spots — Provenance Escape (incl. langchain finding), Output-Context Risk Elevation | Done |
| VII | Doctrinal analysis — Art. 52 vs GDPR, three-instrument package, China comparison | Done |
| VIII | Policy recommendations R1–R4 | Done |
| IX | Threats to validity (incl. Jurisdictional validity para) | Done |
| X | Conclusion | Done |
| XI | Ethical and legal considerations | Done |
| References | [1]–[16] | Done |

### Key findings

- E1: 0–10% Art. 52 compliance across 43,816 Copilot-configured repos
- E2: Headers survive all formatters; destroyed by `.pyc` compilation and comment stripping
- E3: 0.000% compliance across 18,210 Python files from 25 major PyPI packages
- JS (TABLE V): 3/20 sampled repos EU-established (Tier 1); 0 extraterritorial (Tier 2)
- JS (TABLE VI): 23/25 E3 packages exceed 5% EU download threshold; langchain anomaly (1.9%) discussed in VI.A

## Experiments and scripts

All in `tmp/`:

| Script | What it does |
|---|---|
| `jurisdiction_experiment.py` | Classifies E1 repo sample by Art. 2 tier (GitHub API + city-name lookup) |
| `pypi_eu_downloads.py` | Queries BigQuery `pypi.file_downloads` for EU-27 share per package |
| `jurisdiction_results.json` | Raw output from jurisdiction_experiment.py |
| `pypi_eu_results.json` | Raw output from pypi_eu_downloads.py |

### Re-running the experiments

**GitHub (jurisdiction_experiment.py):** requires `gh` CLI authenticated as VinitaSilaparasetty — already set up.

**PyPI BigQuery (pypi_eu_downloads.py):** requires Google Cloud service account key.
- Key file: `~/Downloads/pr-automation-501712-4666cdba9f6b.json` (NOT committed — keep secret)
- Project: `pr-automation-501712`
- The script uses a 1-day query window to stay within the BigQuery free-tier quota (~50–100 GB scanned)

## What's next

The paper content is complete. Remaining steps for submission:
1. Convert `paper.md` to IEEE LaTeX using `IEEEtran.cls` (two-column, 10pt, US letter)
2. Verify page count ≤ 10 body + 2 references
3. Submit to MSR or ICSE

## Python environment

```
python3 -m pip install langdetect google-cloud-bigquery
```
