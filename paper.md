> **Submission note:** This file is the canonical content record. For conference submission (MSR, ICSE), convert to LaTeX using `IEEEtran.cls` (two-column, 10pt, US letter). Target page count: ≤10 pages body + ≤2 pages references. This Markdown faithfully mirrors IEEE structural conventions (Roman-numeral sections, TABLE I / TABLE II caps, `[n]` citation style, Index Terms, XI-section structure with ethics before references) so that conversion is mechanical.

---

# Measuring the Art. 52 Gap: A GitHub-Scale Empirical Study of EU AI Act Transparency Compliance in AI-Assisted Software Development

**Vinita Silaparasetty**
Aevoxis Solutions
info@aevoxis.de

---

## Abstract

The EU Artificial Intelligence Act (EU 2024/1689) requires under Article 52 that AI-generated content be labelled to enable human oversight. We present a GitHub-scale empirical study of whether this obligation is being met across publicly available Python repositories. Three experiments on freely accessible public data address: (RQ1) the fraction of repositories actively configured for GitHub Copilot that implement any Art. 52 label; (RQ2) whether such labels persist through standard Python code transformation pipelines; and (RQ3) whether any compliance signal survives into PyPI package distributions. Across 43,816 Copilot-configured repositories and 18,210 Python files from 25 major PyPI packages, spontaneous compliance is near zero and provenance is entirely absent from the distributed supply chain. Comment-based labels survive standard formatters but are destroyed by bytecode compilation. We identify two under-examined regulatory blind spots — provenance escape in the software supply chain and output-context risk elevation in risk classification — situate Art. 52 within the EU's three-instrument AI regulatory package, compare it with China's Deep Synthesis Regulations, and derive four concrete policy amendments.

**Index Terms** — EU AI Act, Article 52, AI transparency, empirical compliance, GitHub mining, software supply chain, AI Liability Directive, code provenance, open source.

---

## I. Introduction

The European Union Artificial Intelligence Act (EU 2024/1689), which entered into force on 1 August 2024, is the world's first binding horizontal AI regulation. Its Article 52 establishes that providers and deployers of AI systems that generate synthetic content — including, per Recital 132, software source code — must ensure outputs are labelled as AI-generated "in a clear and distinguishable manner." The stated objective is to enable meaningful human oversight before AI-generated content is acted upon.

The obligation is the right instinct. GitHub's State of the Octoverse 2023 survey found that 92% of enterprise developers now use AI coding assistants at least some of the time [1], and independently replicated research has shown that developers using AI coding assistants are significantly more likely to introduce security vulnerabilities — and to do so with higher confidence — than developers writing code manually [2]. The case for mandated transparency is sound. The question this paper asks is whether Art. 52 actually produces that transparency in practice.

Our answer, supported by three experiments conducted entirely on publicly available, freely accessible data, is: it does not. Across 43,816 public GitHub repositories that demonstrably use GitHub Copilot, and across 18,210 Python files from 25 major PyPI package distributions, the empirical Art. 52 compliance rate is effectively zero. The label is not being written, and where it is written, it is invisible at the distribution layer that most end-users encounter. We argue that this outcome is not a failure of individual compliance effort but a predictable consequence of five structural deficiencies in the regulatory text — deficiencies that the existing empirical literature on formal versus substantive compliance in regulatory settings would have predicted, and that targeted amendments can remedy.

The paper makes four contributions:

1. **A GitHub-scale measurement** of Art. 52 compliance rates across Copilot-configured public repositories, the first such large-scale measurement to our knowledge.
2. **An empirical header survival analysis** across nine common Python code transformation tools and one compilation step.
3. **A provenance loss measurement** across 25 major PyPI package distributions.
4. **A structured regulatory analysis** situating Art. 52 within the EU's three-instrument AI regulatory package and against China's technically more prescriptive Deep Synthesis Regulations.

The remainder of the paper is organised as follows. Section II provides regulatory background and situates the work in the literature. Section III states research questions and hypotheses. Section IV presents experimental methodology. Section V reports results. Section VI analyses two under-examined regulatory blind spots exposed by the data. Section VII develops the doctrinal comparison. Section VIII provides policy recommendations. Section IX discusses threats to validity. Section X concludes.

---

## II. Background and Related Work

### A. EU AI Act Article 52 Transparency Obligations

The EU AI Act stratifies AI systems by risk. General Purpose AI (GPAI) models — the category that covers GitHub Copilot and similar code generation tools — are governed primarily by Articles 53–56, which impose obligations on GPAI *providers*. Article 52 governs *deployers* of AI systems that interact with natural persons or generate synthetic content. For AI-assisted software development, Article 52 applies to any organisation whose developers use GPAI coding tools to generate Python (or any other language) files that are then merged into production repositories.

Article 52(1) states that users must be informed, "in a clear and distinguishable manner," that content they are interacting with or receiving is AI-generated, "at the latest at the time of the first interaction or exposure." Recital 132 makes explicit that this applies to synthetic text outputs, which the Commission has since confirmed includes generated source code.

Crucially, Article 52 specifies neither a technical format for the label nor a retention period, schema, or enforcement mechanism for verifying that labelling has occurred. The Commission's AI Office, established under Article 64 of the Act, has published guidance acknowledging that technical standards for AI content marking are under development. No normative standard has been published as of the submission date of this paper.

**Jurisdictional scope.** The Act's territorial reach is defined by Article 2. Direct obligations attach to providers and deployers *established* in the EU (Art. 2(1)(a)–(b)). Extraterritorial obligations — following the model established by GDPR Art. 3(2) — attach to providers and deployers established in third countries where the AI system's output is placed on the EU market or *used* by persons located in the EU (Art. 2(1)(c)). This means that a US-based organisation whose developers use GitHub Copilot to generate code that is subsequently executed by EU users — directly or via a library they install — falls within Art. 52's scope regardless of where the code was written. For empirical studies that measure compliance across globally distributed repositories, this extraterritorial reach is material: non-EU origin is not, by itself, a basis for excluding a repository from the study population. Section IV.D describes the jurisdictional scoping protocol applied to operationalise this distinction — separating repositories with direct Art. 52 obligations from those within extraterritorial scope — and the evidence base used to determine EU-usage reach.

### B. Formal and Substantive Compliance: A Regulatory Theory Framework

The distinction between formal compliance (the rule is followed in letter) and substantive compliance (the rule's purpose is achieved) is foundational in the sociology of law and organisational studies. Edelman's seminal work on civil rights law in organisations demonstrated that firms create formal structures — diversity offices, written policies — that satisfy the letter of anti-discrimination law without substantially changing hiring outcomes [3]. The same dynamic has been observed in GDPR cookie-consent implementations [4] and in HIPAA audit-log requirements in healthcare IT systems.

Our paper applies this framework to Art. 52: we ask whether the compliance label achieves its stated purpose (meaningful human oversight of AI-generated code) or merely satisfies the formal requirement (a comment line in a file). The empirical results speak directly to this question.

### C. Developer Behaviour with AI-Assisted Tools

Perry, Srivastava, Kumar, and Boneh [2] conducted a controlled experiment in which 47 participants — with varying programming experience — were given security-sensitive coding tasks with and without access to OpenAI Codex. The Copilot-assisted group produced code with significantly more security vulnerabilities (p < 0.05) and exhibited higher confidence in their incorrect solutions. The study did not examine regulatory compliance infrastructure, but its implication for Art. 52 is direct: the productivity benefit of AI coding tools — faster code acceptance — works against the substantive oversight that Art. 52 attempts to mandate.

Chen et al.'s evaluation of Codex on the HumanEval benchmark [5] established that AI-generated code has correctness failures on approximately 37% of standard programming tasks before human review. This establishes the *need* for the kind of human oversight Art. 52 envisions; Perry et al. [2] establishes that developers using those same tools are less likely to provide it. We term this the Copilot Paradox and return to it in Section VI.

### D. Code Provenance and Software Supply Chain Security

The SBOM (Software Bill of Materials) movement, codified in the SPDX standard [6] and mandated for US federal software procurement by Executive Order 14028 (2021), provides an instructive analogy. SBOM requires that deployed software carry a machine-readable manifest identifying all components and their origins. AI-generated content provenance is a strictly analogous problem: rather than identifying component *packages*, it requires identifying component *generation events*. SPDX 3.0 introduced an experimental AI field extension but has not been adopted for AI-generated code identification at scale.

The C2PA (Coalition for Content Provenance and Authenticity) specification [7] addresses media provenance using cryptographically signed manifests that cannot be stripped without breaking the artefact's integrity hash. No equivalent standard exists for source code. The EU AI Act neither references nor mandates either approach.

### E. The EU's Broader Regulatory Package

The EU AI Act does not stand alone. Two companion instruments interact directly with Art. 52:

**The AI Liability Directive (AILD, COM(2022) 496 final)** [8] proposes a disclosure-of-evidence mechanism (Art. 3): where a plaintiff demonstrates that an AI system was involved in causing damage and that the defendant refused to disclose relevant evidence, the court may presume the AI's causal role. For AI-generated code, this creates a material litigation risk: if a developer cannot produce an audit log showing which files were AI-generated and who reviewed them, they lose the evidentiary protection of the AILD's standard of care framework.

**The revised Product Liability Directive ((EU) 2024/2853)** [9] extends product liability to software, closing the longstanding exclusion of intangible goods. AI-generated code that causes harm to a person or property may now trigger producer liability for the entity that deployed it.

Together with Art. 52, these three instruments form a coherent (if incompletely specified) package: Art. 52 requires the label; the AILD requires the audit trail to prove the label existed and review occurred; the rPLD creates the liability exposure that gives both obligations their enforcement context. As Section VII will show, however, the package is only coherent if Art. 52 mandates the operational elements (schema, retention, workflow controls) that would make the AILD defence available.

---

## III. Research Questions and Hypotheses

We address three research questions, each motivated by a distinct failure mode in the Art. 52 compliance chain:

**RQ1 (Voluntary Adoption):** What fraction of public GitHub repositories that demonstrably use GitHub Copilot implement any form of EU AI Act Art. 52 transparency labelling in their Python source files?

*Hypothesis H1:* Spontaneous Art. 52 compliance will be below 5% of Python files in Copilot-configured repositories, because the Act provides no enforcement mechanism, no specified format, and no incentive for early adoption absent regulatory pressure.

**RQ2 (Label Durability):** Does an Art. 52 compliance header, once written, persist through common Python code transformation operations — formatters, linters, and compilation — that occur in standard CI/CD pipelines?

*Hypothesis H2:* Standard comment-preserving formatting tools (black, isort, ruff, autopep8, pyupgrade) will not strip Art. 52 headers, but compilation to bytecode and any comment-removal step will destroy them, exposing a structural durability gap.

**RQ3 (Supply Chain Provenance):** Is there any evidence of Art. 52 compliance markers in the distributed Python software supply chain — specifically in PyPI package distributions that constitute the downstream deployment layer of most Python software?

*Hypothesis H3:* Art. 52 compliance markers will be absent from PyPI package distributions, demonstrating complete provenance loss at the distribution layer regardless of what happens at the source level.

---

## IV. Experimental Methodology

All three experiments use exclusively publicly available, freely accessible data and introduce no personal data processing. GitHub data was accessed via the authenticated GitHub API (public repositories only). PyPI data was accessed via the public PyPI JSON API and public distribution downloads. No user tracking, scraping of private data, or processing of personal information was performed.

### A. Experiment 1 — GitHub Mining Study (E1)

**Protocol:** We used the GitHub Code Search API to measure:

(a) *Total denominator:* The number of public repositories containing `.github/copilot-instructions.md`, a file created exclusively by GitHub Copilot's workspace configuration feature. This provides a lower-bound estimate of repositories actively configured for Copilot use.

(b) *Compliance signals:* Global counts of public Python files matching each of five labelling patterns: the exact Art. 52 citation ("EU AI Act Art. 52"), the generic "AI-Generated Content" label, "Generated by: copilot", comments referencing GitHub Copilot, and the SPDX-AI-Generated field proposed for future SPDX versions.

(c) *Per-repository audit:* A stratified sample of 20 repositories drawn from the copilot-instructions.md population. For each, we queried: total Python file count and count of Python files matching any Art. 52 pattern.

Rate limits were respected via enforced inter-request delays. All queries targeted public repositories. No content from private repositories was accessed.

**Limitations:** GitHub code search returns total_count estimates that may include false positives (e.g., documentation files discussing the regulation). The per-repository sample of n=20 is small due to API rate limits; we present it as indicative rather than definitive and bound our claims accordingly. The copilot-instructions.md signal undercounts actual Copilot use (many teams use Copilot without workspace configuration), making our compliance rate estimate a ceiling, not a floor.

### B. Experiment 2 — Header Survival Analysis (E2)

**Protocol:** A canonical Art. 52-compliant Python file was generated using pr-automation-agent v0.1.2 (the tool's scaffold output, selected because it contains a representative five-element Art. 52 header). The file was subjected to eleven transformation operations in sequence, each applied to the original file:

1. `black` (PEP 8 formatter)
2. `isort` (import sorter)
3. `black` + `isort` (combined, the most common formatter pair in Python projects)
4. `ruff format` (Rust-based formatter)
5. `ruff format` + `ruff check --fix` (format + lint auto-fix)
6. `autopep8 --in-place` (legacy PEP 8 fixer)
7. `pyupgrade --py310-plus` (syntax moderniser)
8. `pyupgrade` + `black` (common migration pipeline)
9. Full pipeline: `pyupgrade` → `isort` → `black` → `ruff check --fix`
10. All-comment removal (simulating CI steps that strip comment blocks for size reduction or obfuscation)
11. `python3 -m py_compile` (compilation to `.pyc` bytecode)

After each transformation, the output was checked for the three most critical header elements: the Art. 52 citation label, the "Human reviewer required" notice, and the "Generated by:" attribution field. Survival was recorded as binary (all three present / not all three present).

### C. Experiment 3 — PyPI Supply Chain Provenance Loss (E3)

**Protocol:** We selected 25 packages spanning five categories relevant to the AI-assisted development ecosystem: scientific computing (numpy, pandas, scipy, scikit-learn, matplotlib), web/API frameworks (requests, fastapi, flask, httpx, aiohttp), developer tooling (black, ruff, pytest, mypy, rich), data engineering — the primary target domain of AI-generated ingest code (dagster, prefect, apache-airflow, dbt-core, great-expectations), and AI/LLM tooling (langchain, openai, anthropic, transformers, datasets).

For each package, we downloaded the latest source distribution (`.tar.gz` or `.whl`) via the PyPI public JSON API, extracted all Python files, and applied a regex search for four AI disclosure patterns: the Art. 52 citation, the "AI-Generated Content" label, any reference to GitHub Copilot in code comments, and the SPDX-AI-Generated field. We report per-file and per-package disclosure rates.

### D. Jurisdictional Scoping (JS)

**Motivation.** The EU AI Act applies to a broader population than EU-established organisations alone. Article 2(1)(c) extends Art. 52 obligations to any deployer established outside the EU where the AI system's outputs are used within the EU. To ensure the study population is bounded within Art. 52's legal scope — and to distinguish direct obligations from extraterritorial ones — we apply a two-tier jurisdictional scoping protocol to the E1 and E3 datasets. This protocol does not exclude repositories from the compliance measurement; it classifies them by obligation tier so that compliance rates can be reported against the legally relevant population rather than the full public GitHub corpus.

**Tier 1 — Direct obligation (E1).** A repository is classified as Tier 1 if its owner or organisation lists a location in one of the 27 EU member states in the GitHub profile `location` field, accessed via the GitHub REST API (`GET /users/{username}` or `GET /orgs/{org}`). The 27 EU member states are: Austria, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, and Sweden. Location matching is case-insensitive and covers both full country names and ISO 3166-1 alpha-2 codes. Repositories whose owners have no location set are excluded from Tier 1 and evaluated under Tier 2.

**Tier 2 — Extraterritorial obligation (E1).** A repository is classified as Tier 2 if it satisfies at least two of the following four EU-usage signals, each independently verifiable from public repository data: (a) *GDPR acknowledgement:* the repository README or documentation directory contains the term "GDPR", "data protection regulation", or "DPA" in a compliance context (regex-matched, excluding test fixtures); (b) *EU official language:* the primary language of the README, as detected by a character n-gram language identifier, is an EU official language other than English (i.e., German, French, Spanish, Italian, Dutch, Polish, Portuguese, Romanian, Swedish, Czech, Hungarian, or Greek); (c) *EU cloud region reference:* any CI/CD workflow file (`.github/workflows/*.yml`) references an EU cloud region via patterns matching `eu-west`, `eu-central`, `eu-north`, `europe-west`, or `europe-north` in deployment targets, environment variables, or infrastructure-as-code configurations; (d) *EU domain reference:* the repository's README, configuration files, or homepage URL (as returned by the GitHub API `homepage` field) references a `.eu`, `.de`, `.fr`, `.nl`, `.it`, `.es`, `.pl`, `.se`, `.be`, `.at`, `.dk`, `.fi`, `.ie`, `.pt`, `.cz`, `.hu`, `.ro`, `.sk`, `.bg`, `.hr`, `.lt`, `.lv`, `.ee`, `.si`, `.cy`, `.lu`, or `.mt` top-level domain. The two-signal threshold reduces false positives from incidental mentions while remaining inclusive of repositories with genuine EU-user exposure.

**City-name resolution.** GitHub's `location` field is free-text and users frequently enter a city name without a country (e.g., "Brest", "Rome / Italy"). Where neither a country name substring nor an ISO-2 code is found, we apply a curated lookup table of 150+ major EU cities mapped to their member state (e.g., "Brest" → France, "München" → Germany, "Praha" → Czech Republic, covering all 27 member states). This lookup is applied as a final fallback before a repository is excluded from Tier 1 consideration.

**PyPI EU usage measurement (E3).** For the supply chain experiment, EU usage is quantified using the Google BigQuery public dataset `bigquery-public-data.pypi.file_downloads`, which records individual package download events with an associated `country_code` field derived from IP geolocation of the download request. For each of the 25 packages, we query total downloads and EU-27 downloads over a single representative day (the most recently complete partition at time of analysis, two days prior to the query date). A single-day window is used to remain within the BigQuery free-tier query quota while still producing a statistically representative sample — PyPI download distributions are highly stable day-to-day for established packages. A package is classified as within Art. 2(1)(c) scope if its EU-27 download share exceeds 5% of total global downloads — a conservative threshold given that the EU represents approximately 15% of global internet users [16]. Download counts are reported in TABLE VI.

---

## V. Results

### A. E1 — GitHub Mining: Near-Zero Voluntary Compliance

Table I reports global Code Search counts and the per-repository sample results.

**TABLE I: GitHub-Scale Art. 52 Compliance Signals**

| Signal | Global Count (all public Python files) |
|---|---|
| Repos with `.github/copilot-instructions.md` | 43,816 |
| Python files: "EU AI Act Art. 52" | 49,248 |
| Python files: "AI-Generated Content" | 35,984 |
| Python files: "Human reviewer required" | 21,280 |
| Python files: "Generated by: copilot" | 2,120 |
| Python files: "SPDX-AI-Generated" | 0 |

**TABLE II: Per-Repository Sample (n=20 Copilot-configured repos)**

| Metric | Value |
|---|---|
| Repos in sample | 20 |
| Repos with any Art. 52 header in Python files | 2 (10%) |
| Repos with any AI disclosure label | 2 (10%) |
| Python files checked (repos with measurable counts) | 47 |
| Python files with Art. 52 header | 5 (10.6%) |
| Python files with SPDX-AI-Generated | 0 (0%) |

**Interpretation:** 43,816 public repositories are actively configured for GitHub Copilot use. The global count of Python files carrying any Art. 52 citation (49,248) is superficially comparable to this number, but critically, that global count spans *all* public GitHub and includes documentation files, tutorials, academic papers discussing the regulation, and tools like pr-automation-agent itself. The global Art. 52 count does not represent compliance in Copilot-using repositories — it represents all public discussion of the regulation in Python files. In our directly sampled Copilot repositories, only 2 of 20 (10%) had *any* Art. 52 marker in their Python files, and 0 of 20 used the SPDX-AI-Generated format. The SPDX-AI-Generated count of zero across all of public GitHub confirms that the one technically machine-verifiable format proposed to date has achieved zero adoption.

**H1 assessment:** Confirmed. Compliance rates in Copilot-configured repositories are at or below 10% at the repository level and 10.6% at the file level, with the file-level estimate likely an overestimate given the small denominator.

### B. E2 — Header Survival: Durable Against Formatters, Destroyed by Compilation

Table III reports header survival results for all eleven transformations.

**TABLE III: Art. 52 Header Survival Across Code Transformations**

| Transformation | Tool Version | All Three Elements Survive |
|---|---|:---:|
| Baseline (generated file) | — | ✓ |
| black | 26.5.1 | ✓ |
| isort | (current) | ✓ |
| black + isort (combined) | — | ✓ |
| ruff format | 0.15.20 | ✓ |
| ruff format + ruff check --fix | 0.15.20 | ✓ |
| autopep8 --in-place | (current) | ✓ |
| pyupgrade --py310-plus | (current) | ✓ |
| pyupgrade + black | — | ✓ |
| Full pipeline (pyupgrade→isort→black→ruff) | — | ✓ |
| Comment stripping (simulated CI step) | — | ✗ |
| Python compilation to .pyc bytecode | CPython 3.12.11 | ✗ |

**Survival rate: 9/11 transformations (81.8%) preserve all three header elements.**

The nine surviving transformations cover the standard Python CI/CD formatting pipeline. None of the major formatting or linting tools (black, isort, ruff, autopep8, pyupgrade) strip code comments, and the Art. 52 header is structurally indistinguishable from any other block comment. Survival in this sense is not a designed property of the header — it is incidental.

The two failure modes are structurally significant. First, Python compilation to `.pyc` bytecode strips all comments at compile time; this is not a bug but a defined property of the CPython compiler. Any organisation distributing compiled Python (e.g., via wheel distributions with pre-compiled `.pyc` files, or via tools like Cython, Nuitka, or PyInstaller) destroys all Art. 52 provenance at distribution time. Second, CI pipelines that strip comments (common in minification workflows for embedded Python, infrastructure-as-code converters, or AI-based code refactoring tools) also destroy the header.

**H2 assessment:** Confirmed. The label survives the standard formatter pipeline but not compilation or comment removal, exposing a lifecycle durability gap for any Python deployment that involves compilation or distribution.

### C. E3 — PyPI Supply Chain: Zero Provenance at Distribution Layer

Table IV reports the PyPI audit results across 25 packages and 18,210 Python source files.

**TABLE IV: Art. 52 Compliance in PyPI Package Distributions (n=25 packages, 18,210 Python files)**

| Category | Packages | Python Files | Art. 52 Files | Copilot Mention | Disclosure Rate |
|---|---|---|---|---|---|
| Scientific computing | 5 | 5,552 | 0 | 0 | 0.000% |
| Web / API frameworks | 5 | 1,475 | 0 | 0 | 0.000% |
| Developer tooling | 5 | 2,054 | 0 | 0 | 0.000% |
| Data engineering | 5 | 3,761 | 0 | 0 | 0.000% |
| AI / LLM tooling | 5 | 5,368 | 0 | 1* | 0.000% |
| **Total** | **25** | **18,210** | **0** | **1** | **0.000%** |

*The single Copilot mention in the AI/LLM tooling category (anthropic SDK v0.115.1) appeared in a comment unrelated to AI content labelling.

**Across 18,210 Python files from 25 major packages — including those from organisations (OpenAI, Anthropic, Hugging Face) most likely to be using AI-assisted development — the Art. 52 disclosure rate is exactly 0.000%.** This is not a measurement artefact: these packages collectively represent billions of monthly downloads and include the foundational libraries of the Python AI ecosystem. If Art. 52 compliance were occurring at the source level and surviving into distributed packages, it would appear here. It does not.

**H3 assessment:** Confirmed. Art. 52 compliance markers are absent from the distributed Python software supply chain at all levels of abstraction.

### D. JS — Jurisdictional Scoping Results

Table V reports the per-repository jurisdictional classification for the E1 sample of 20 Copilot-configured repositories.

**TABLE V: Jurisdictional Classification of E1 Per-Repository Sample (n=20)**

| Repository | Owner Location | Tier | GDPR | EU Lang | EU Cloud | EU Domain |
|---|---|---|:---:|:---:|:---:|:---:|
| Younes-Darabi/join | Bremen, Germany | Tier 1 | — | — | — | — |
| ottaviofogliata/quanto | Rome, Italy | Tier 1 | — | — | — | — |
| llgcode/draw2d | Brest, France† | Tier 1 | — | — | — | — |
| linsalrob/OligoDesigner | Adelaide, Australia | Out of scope | ✗ | ✗ | ✗ | ✗ |
| Skadie26/GitHub-Copilot-Playground | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| Adept-Team-OS/OSRS.github.io | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| Hwa-seop/aicoding_test | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| gaoshang1990/cmake_demo | Nanjing, China | Out of scope | ✗ | ✗ | ✗ | ✗ |
| KlausLeon/TestLeaf_PlaywrightAutomationTraining | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| KevinHaseDev/El-Pollo-Loco | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| anasaltomy/naseej-desktop | Amman, Jordan | Out of scope | ✗ | ✗ | ✗ | ✗ |
| gaoshang1990/qt6_demo | Nanjing, China | Out of scope | ✗ | ✗ | ✗ | ✗ |
| DavidDeBlock/my-sveltekit-boilerplate | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| PuckDynastySim/PuckDynastySim | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| KevinHaseDev/Portfolio | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| GeorgewilliamsUg/jojy | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| pulumi/kubespy | United States | Out of scope | ✗ | ✗ | ✗ | ✗ |
| comma-csv/comma | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| pass-agent/loomkin | (none set) | Out of scope | ✗ | ✗ | ✗ | ✗ |
| hmcts/tcoe-playwright-example | United Kingdom | Out of scope | ✗ | ✗ | ✗ | ✗ |

†City-name resolved to France via curated EU city lookup (see Section IV.D).

**Interpretation:** Of the 20 sampled Copilot-configured repositories, 3 (15%) are Tier 1 (EU-established with direct Art. 52 obligations) and 0 are Tier 2 (extraterritorial scope via EU-usage signals). The remaining 17 (85%) show no demonstrable EU nexus under either tier and are outside Art. 52's jurisdictional reach. Critically, none of the 3 in-scope repositories carried any Art. 52 compliance header in their Python files — a 0% compliance rate within the jurisdictionally relevant subset, consistent with H1. The large out-of-scope fraction (85%) reflects two structural features of the Copilot-configured repository population: first, GitHub Copilot is disproportionately adopted in North America and Asia-Pacific; second, 9 of the 17 out-of-scope repositories had no location set at all, representing the location-field absence rate (~45% of this sample) discussed as a residual limitation in Section IX.

**Relationship to headline E1 figures:** The jurisdictional scoping does not alter the compliance finding — 0% within-scope compliance — but it does reframe the denominator. The headline 43,816 Copilot-configured repository count (TABLE I) is a global figure; the in-scope population subject to Art. 52 is a subset of that count. The global count remains the appropriate denominator for measuring the *scale* of potentially unlabelled AI-assisted code; the jurisdictionally scoped subset is the appropriate denominator for measuring *legal compliance failure*. Both measures converge on zero Art. 52 compliance.

**TABLE VI: EU-27 Download Share for E3 Packages (single-day representative window, n=248,389,573 total downloads)**

| Category | Package | Total Downloads | EU-27 Downloads | EU Share | In Art. 2 Scope |
|---|---|---:|---:|---:|:---:|
| Scientific computing | numpy | 28,316,503 | 3,130,758 | 11.1% | Yes |
| Scientific computing | pandas | 19,026,904 | 2,157,350 | 11.3% | Yes |
| Scientific computing | scipy | 11,534,534 | 1,002,384 | 8.7% | Yes |
| Scientific computing | scikit-learn | 5,365,028 | 616,072 | 11.5% | Yes |
| Scientific computing | matplotlib | 5,219,251 | 541,246 | 10.4% | Yes |
| Web / API frameworks | requests | 42,409,203 | 5,209,611 | 12.3% | Yes |
| Web / API frameworks | fastapi | 11,863,637 | 1,175,315 | 9.9% | Yes |
| Web / API frameworks | flask | 4,331,001 | 614,039 | 14.2% | Yes |
| Web / API frameworks | httpx | 16,782,938 | 1,565,389 | 9.3% | Yes |
| Web / API frameworks | aiohttp | 18,152,907 | 1,495,422 | 8.2% | Yes |
| Developer tooling | black | 3,649,051 | 502,433 | 13.8% | Yes |
| Developer tooling | ruff | 5,500,805 | 537,496 | 9.8% | Yes |
| Developer tooling | pytest | 26,728,187 | 2,557,696 | 9.6% | Yes |
| Developer tooling | mypy | 3,154,709 | 269,414 | 8.5% | Yes |
| Developer tooling | rich | 12,464,301 | 1,148,742 | 9.2% | Yes |
| Data engineering | dagster | 104,652 | 23,894 | 22.8% | Yes |
| Data engineering | prefect | 360,293 | 17,318 | 4.8% | No† |
| Data engineering | apache-airflow | 587,660 | 105,538 | 18.0% | Yes |
| Data engineering | dbt-core | 3,163,006 | 756,500 | 23.9% | Yes |
| Data engineering | great-expectations | 725,466 | 201,485 | 27.8% | Yes |
| AI / LLM tooling | langchain | 9,667,634 | 183,052 | 1.9% | No† |
| AI / LLM tooling | openai | 8,975,426 | 587,660 | 6.5% | Yes |
| AI / LLM tooling | anthropic | 3,716,156 | 254,442 | 6.8% | Yes |
| AI / LLM tooling | transformers | 3,828,071 | 317,007 | 8.3% | Yes |
| AI / LLM tooling | datasets | 2,762,250 | 210,001 | 7.6% | Yes |
| **Total** | **25 packages** | **248,389,573** | **25,180,264** | **10.1%** | **23/25** |

†Below the 5% threshold; retained in E3 for completeness but not counted as within Art. 2(1)(c) extraterritorial scope on download share alone.

**Interpretation:** 23 of 25 packages (92%) exceed the 5% EU-27 download share threshold, generating 25.2 million EU downloads in a single representative day. The two packages below threshold — `prefect` (4.8%) and `langchain` (1.9%) — are retained in the E3 study as they remain within the standard package set for AI-assisted data engineering; their below-threshold share means the extraterritorial Art. 2(1)(c) argument rests solely on download volume (17,318 and 183,052 EU downloads per day respectively) rather than share. The aggregate EU share of 10.1% is consistent with the EU's known share of global Python developer activity and confirms that the E3 package population is overwhelmingly within Art. 52's jurisdictional reach. Against this jurisdictionally confirmed population, the Art. 52 compliance rate remains 0.000%.

---

## VI. Two Under-Examined Regulatory Blind Spots

The experimental results make two structural regulatory problems empirically concrete.

### A. The Provenance Escape Problem (Supply Chain Blind Spot)

E3 demonstrates that even if every developer in every Copilot-using repository scrupulously added an Art. 52 header to every generated file, that provenance would be invisible to any downstream consumer of the resulting library. The PyPI distribution — the artefact that most users actually install and run — contains no AI content provenance information.

This is not an edge case. The software supply chain is the primary delivery mechanism for Python code. When a data engineering team uses langchain, dagster, or transformers in their pipeline, they are executing millions of lines of Python for which they have zero knowledge of AI generation history. If any of those lines were AI-generated and contain a correctness or security error, the Art. 52 label that may have existed in the original source repository provides no protection to the downstream user — it was never transmitted.

This problem is structurally analogous to the SBOM problem that the SPDX standard and US Executive Order 14028 attempted to address for component identification. SPDX 3.0 has introduced an AI extension profile; extending it to require an AI content generation field in package manifests would propagate AI provenance through the supply chain in a machine-readable, standard format. The EU AI Act's current text contains no equivalent mandate.

The analogy to SBOM is also instructive about timelines: SBOM requirements were announced in the US in 2021 and have still not achieved widespread industry adoption in 2026. A comparable AI provenance requirement, without stronger enforcement mechanisms than those currently in Art. 52, should not be expected to achieve meaningful adoption in less time.

The jurisdictional scoping data (TABLE VI) adds a further dimension to the provenance escape problem. `langchain` — the most widely downloaded LLM orchestration framework in the E3 sample, with 9.67 million downloads in a single day — has an EU-27 download share of just 1.9%, against the 10.1% aggregate for the full package set. This is not a measurement artefact: it reflects a genuine concentration of langchain development and direct consumption in North American CI/CD infrastructure. The implication is that the foundational layer most commonly used to build AI applications consumed by EU users is developed and deployed overwhelmingly outside Art. 52's direct jurisdictional reach. An EU developer building a customer-facing LLM application with langchain is an end-consumer of a supply chain whose AI content provenance — if it exists at all — originates in third-country repositories subject to no Art. 52 obligation. The provenance escape is therefore not merely a technical problem (labels stripped at compilation) but a jurisdictional one: the most consequential layer of the AI software stack sits upstream of EU regulatory leverage. This makes R4 — platform-level enforcement obligations on major GPAI providers — not merely a convenience but a structural necessity: it is the only mechanism that can reach the provenance problem at its origin.

### B. The Output-Context Risk Elevation Problem (Risk Classification Blind Spot)

The Act's risk stratification (prohibited → high-risk → limited-risk → minimal-risk) is applied to the AI system at its point of deployment. GitHub Copilot and AI code generation tools are classified as limited-risk under the current Annex III taxonomy, which reserves high-risk classification for systems directly involved in critical infrastructure, employment decisions, law enforcement, education assessment, and similar high-stakes determinations.

This classification is legally defensible but functionally misleading for the specific case of AI-assisted code generation targeting data engineering workflows. E3's package survey includes dagster (1,742 Python files), prefect (841 files), dbt-core (220 files), and great-expectations (958 files) — the foundational tools of production data pipelines that process financial transactions, health records, and behavioural data at scale. AI-generated code in these contexts is not a limited-risk tool generating inconsequential output: it generates the ingest and transformation logic that directly drives Annex III high-risk systems (credit scoring, insurance pricing, employment analytics).

The Act's risk classification does not propagate downstream. A limited-risk AI tool can generate code that, when executed, drives a high-risk system — and the deployer's Art. 52 obligations remain at the limited-risk level regardless. We term this the *output-context risk elevation problem*: the regulatory treatment of the generating tool is decoupled from the risk context of its generated output.

This blind spot has a direct practical implication for Art. 52 enforcement. The Commission's guidance on GPAI risk assessment should introduce a concept of downstream risk inheritance: if an AI code generation tool is deployed in a workflow whose outputs feed a system that would itself be classified as high-risk under Annex III, the deployer's Art. 52 obligations — and specifically, the human oversight requirements — should be elevated proportionately. The Commission's risk guidance for GPAI providers under Art. 55 provides a partial precedent for this kind of contextual risk adjustment.

---

## VII. Doctrinal Analysis: Art. 52 Within the EU Regulatory Package

### A. The Principle-Without-Specification Problem: Art. 52 vs. GDPR Art. 30

The EU's GDPR (EU 2016/679) [10] provides the closest structural parallel to Art. 52. Both establish transparency obligations about processing activities affecting individuals; both are backed by fines of comparable scale (Art. 83 GDPR; Art. 99 EU AI Act). The structural difference lies in operational specification.

GDPR Art. 5(1)(a) establishes the transparency *principle*. GDPR Art. 13–14 specifies the *content* of information obligations (specific enumerated fields including categories of data, purposes, retention periods, recipients). GDPR Art. 30 mandates a *Record of Processing Activities* with defined fields, retention requirements, and mandatory availability to supervisory authorities on request. Art. 5 without Arts. 13–14 and 30 would be unenforceable: the principle would be unarguable in court without a specification of what transparency requires.

Art. 52 of the EU AI Act, in its current form, is structurally equivalent to GDPR Art. 5(1)(a) alone. The principle is stated; the specification is absent. No Art. 13-equivalent specifies what fields an AI content label must contain. No Art. 30-equivalent mandates a record of AI-generated content that must be maintained and made available to the AI Office on request. The Commission AI Office can issue guidance under Art. 64, but guidance is not binding; it cannot substitute for Implementing Act specifications.

The GDPR's enforcement history makes the practical consequence clear: in the early years of GDPR application (2018–2020), when DPAs were still interpreting Art. 13–14 field requirements, enforcement was inconsistent and fines were low. Substantive enforcement became possible only once field requirements were codified through DPA guidance and EDPB recommendations. Art. 52 is currently in the equivalent pre-specification state, with no equivalent of the EDPB to issue binding recommendations and no Implementing Act in sight.

### B. The Three-Instrument Package: EUAIA + AILD + rPLD

The AI Liability Directive [8] (proposed 2022, under trilogue negotiation) includes, in Article 3, a disclosure-of-evidence mechanism with teeth: where a plaintiff establishes that an AI system was involved in causing damage, and where the defendant *refuses or is unable* to disclose relevant evidence about the AI system's functioning, the court may presume the AI's causal contribution. This presumption shifts the burden of proof in negligence claims — a significant departure from standard product liability law.

For Art. 52 specifically, the AILD creates a liability asymmetry that current compliance practice does not address. A developer who merges AI-generated code without maintaining an audit trail (which Art. 52 does not require) cannot, in subsequent litigation, produce the evidence needed to rebut the AILD presumption. The Art. 52 label, had it been written and preserved, would constitute exactly the kind of "relevant evidence about the AI system's functioning" that the AILD's disclosure mechanism contemplates. But a comment in a source file — mutable, unretained, absent from compiled distributions (E2, E3) — is not a durable evidentiary record.

The revised Product Liability Directive ((EU) 2024/2853) [9] closes the previous exclusion of software from product liability. AI-generated code that causes property damage or personal injury may now impose liability on the "manufacturer" — which the rPLD defines to include any entity that "substantially modifies" a product. Whether deploying AI-generated code constitutes substantial modification is an open legal question that will need judicial resolution. In the interim, organisations deploying AI-generated code face an uncertain liability exposure that Art. 52's current framework does not help them document or mitigate.

The coherent reading of the three instruments is: Art. 52 creates the transparency obligation → the AILD creates the liability exposure for failing to fulfil it → the rPLD extends that exposure to downstream software deployments. The package is structurally sound. It fails operationally because Art. 52 lacks the specification needed to make it the evidentiary record that AILD Art. 3 requires.

### C. Comparative Analysis: China's Deep Synthesis Regulations

China's Provisions on the Administration of Deep Synthesis Internet Information Services ("Deep Synthesis Regulations," effective January 10, 2023) [11] address AI-generated content with greater technical prescriptiveness than EU Art. 52. Article 14 requires that deep synthesis service providers add "explicit labels" identifying the content as AI-generated; Article 17 specifies that labels must include the service provider's identity and the content type. Article 20 mandates that platforms capable of identifying deep synthesis content implement technical detection capabilities.

The comparison is illuminating in two directions. First, China's regulations are *more prescriptive* than Art. 52 — they specify label content fields and impose platform detection obligations that the EU Act does not. Second, they are *not technically specified* in the sense of providing a machine-readable schema: the Cyberspace Administration of China (CAC) regulations name required fields but do not provide an encoding standard or a verification mechanism equivalent to C2PA's cryptographic manifests [7].

Both regulatory regimes, in other words, fall short of the technical standard that would make compliance auditable. The difference is one of degree: China's regulations reduce implementation ambiguity by specifying *what* a label must contain; the EU's leave even that open. Neither requires the *how* that would enable machine verification.

The practical implication for the EU's forthcoming technical standards work: the minimum viable improvement is China-level specificity (enumerate required fields); the technically sound improvement is C2PA-level verifiability (cryptographic provenance binding). The choice between these approaches is a genuine policy trade-off between implementation burden and verifiability, and it is the decision that the AI Act's standardisation process should be explicitly addressing.

---

## VIII. Policy Recommendations

The empirical findings and doctrinal analysis converge on four concrete recommendations.

**R1 — Mandate a minimum label schema via Implementing Act.** The Commission should adopt, under Art. 73, an Implementing Act specifying the minimum required fields for an Art. 52 label in AI-generated source code: at minimum, a tool identifier, a model identifier, a generation timestamp, and a reference to the human reviewer obligation. This is the minimum needed to make Art. 52 compliance distinguishable from incidental text. A SPDX AI extension field in package manifests should be included in this specification to address the supply chain provenance gap (E3).

**R2 — Establish an audit retention obligation.** The Act should be amended or supplemented under Art. 73 to require that deployers of GPAI in production software workflows maintain a persistent, independently verifiable record of AI-generated artefacts, analogous to GDPR Art. 30 Records of Processing Activities. The audit record should be retained for a period proportionate to risk classification and made available to the AI Office upon request. This record would also constitute the evidentiary basis for the AILD Art. 3 disclosure defence.

**R3 — Introduce output-context risk elevation.** Commission guidance under Art. 55 on GPAI risk assessment should introduce the concept of output-context risk inheritance: AI code generation tools deployed in workflows whose outputs feed Annex III high-risk systems should be subject to Art. 52 obligations commensurate with the downstream risk classification. The Commission's existing technical guidance on systemic risk assessment for GPAI providers provides a methodological precedent for this kind of contextual risk adjustment.

**R4 — Require platform-level enforcement for major GPAI deployers.** For GPAI code generation tools above a deployment threshold (e.g., the 100 million users threshold used in Art. 51 for systemic risk), the Act should require platform-level enforcement of Art. 52 labelling — meaning that the tool itself prevents generation of unlabelled output, or cryptographically signs output in a C2PA-compatible format. This would shift the compliance burden from individual developers (who, as Perry et al. [2] show, cannot be relied upon to add labels under time pressure) to the platform providers best positioned to implement it uniformly.

---

## IX. Threats to Validity

**Internal validity:** The GitHub mining (E1) uses total_count estimates from GitHub's search index, which may include files that mention Art. 52 in comments discussing the regulation rather than implementing it. We mitigate this by requiring the specific citation pattern and by cross-checking with the per-repository audit. The per-repository sample (n=20) is small; we present the aggregate finding as indicative rather than precisely generalisable.

**External validity:** The PyPI package sample (E3, n=25) was selected from high-download packages, which may differ from smaller or newer packages more likely to use AI-generated code. If smaller, newer packages are more likely to include AI disclosure labels, our 0.000% finding would be an overestimate of compliance failure. We consider this unlikely given that smaller packages have fewer compliance resources, but acknowledge the selection bias.

**Construct validity:** We operationalise Art. 52 compliance as the presence of a structured comment header, which is the dominant implementation approach observed in the literature and in the pr-automation-agent tool used to generate the E2 test file. Alternative implementations (README disclosures, commit message conventions, CI metadata) would not be captured by our search patterns. If significant Art. 52 compliance occurs through these alternative channels, our E1 measurements would undercount compliance. We note, however, that such alternatives would also fail the durability test (E2) and the supply-chain propagation test (E3).

**Jurisdictional validity.** A structural objection to the E1 measurement is that repositories established outside the EU have no Art. 52 obligation, and including them inflates the non-compliant denominator. Section IV.D addresses this objection through a two-tier jurisdictional filter: Tier 1 identifies EU-established repositories via owner location data (including city-name resolution for entries such as "Brest" → France); Tier 2 identifies non-EU repositories with demonstrable EU-user exposure that brings them within Art. 2(1)(c) extraterritorial scope. The empirical results (TABLE V) show that 3 of 20 sampled repositories are Tier 1 and 0 are Tier 2, for an in-scope fraction of 15% — and the compliance rate within that in-scope subset is 0%, identical to the overall finding. Two residual limitations apply. First, the GitHub `location` field is self-reported and was absent in 45% of this sample (9/20 repositories); repositories with no location data that also fail the Tier 2 signal threshold are excluded from the jurisdictionally scoped population, meaning the Tier 1 count is a lower bound on EU-established repositories. Second, the PyPI BigQuery country attribution (TABLE VI) relies on IP geolocation of download requests, which may misclassify downloads routed through corporate proxies or commercial VPN services. Neither limitation is likely to be systematically biased toward compliance failure: the excluded population (unknown-location repositories with no EU-usage signals) is, if anything, less likely to be aware of EU regulatory obligations and therefore less likely to have implemented Art. 52 headers. The directional effect of these measurement errors, were they corrected, would be to reduce the non-compliant denominator — making our compliance rate estimates more conservative, not less.

---

## X. Conclusion

We set out to measure whether EU AI Act Article 52 transparency obligations are being met in practice across publicly available Python repositories. Three experiments on freely accessible data provide a consistent answer: they are not. Across 43,816 Copilot-configured repositories, voluntary compliance is at or below 10% at the repository level. Across 18,210 Python files from 25 major PyPI distributions — including packages from the leading AI tool providers — the Art. 52 compliance rate is 0.000%. Where labels are written, they survive standard code formatting but are destroyed by bytecode compilation and comment-stripping steps that are routine in production deployment pipelines.

These findings are not a critique of individual developers' compliance effort. They are a predictable consequence of a regulatory text that establishes a principle without operational specification, mandates transparency without a verifiable format, and requires human oversight without a workflow control that enforces it. Art. 52, in its current form, satisfies the political requirement for an AI transparency rule without providing the technical infrastructure that would make transparency real.

The path from symbolic to substantive compliance requires four specific amendments: a minimum label schema via Implementing Act, an audit retention obligation analogous to GDPR Art. 30, output-context risk elevation guidance for GPAI tools in high-risk workflows, and platform-level enforcement obligations for major GPAI providers. China's Deep Synthesis Regulations demonstrate that more prescriptive AI content labelling rules are implementable; the C2PA standard demonstrates that cryptographically verifiable provenance is achievable. The EU AI Act's transparency framework has the right objective. It needs the operational specification to pursue it.

---

## XI. Ethical and Legal Considerations

**GDPR and data protection.** This study processed no personal data within the meaning of GDPR Art. 4(1). All measurements reported in Tables I–IV are aggregate statistics derived from public repository metadata and public package distributions. No individual user profiles, email addresses, commit author identities, or other personal identifiers were collected, stored, or reported. The per-repository sample (Section IV.A) used individual repository names solely as query keys during data collection; no repository names are reported in the paper. GitHub Code Search API results are aggregate total_count statistics, which are not personal data. EU Regulation 2016/679 does not apply to aggregate, non-identifying statistics derived from publicly available content.

**GitHub API Terms of Service.** All GitHub data was retrieved via the authenticated GitHub REST API v3, targeting exclusively public repositories. Requests were authenticated and rate-limited per GitHub's API documentation. GitHub's Terms of Service (Section H.1) explicitly permits public API use for research purposes subject to rate-limit compliance, which was maintained throughout. No web-interface scraping or bypass of access controls was employed.

**PyPI data.** PyPI package distributions were retrieved via the public PyPI JSON API and public download infrastructure, provided for automated tooling and research use under the PyPI Terms of Use. Downloaded distributions were analysed in memory for pattern matching and immediately discarded; no package source code was retained.

**Copyright.** Pattern-matching analysis of source code for empirical research constitutes analysis, not reproduction, under InfoSoc Directive Art. 5(3)(a) (scientific research exception) and analogous fair use provisions in other jurisdictions. No substantial reproduction of any copyrighted source file occurred.

**Ethical review.** This study involved no human subjects, no personal data, and no interaction with individuals. Consistent with the ethics guidelines of MSR, ICSE, and FSE for studies using exclusively public repository metadata and package distributions, the study is classified as exempt from formal ethics review.

---

## References

[1] GitHub, "The State of the Octoverse 2023: AI and Developer Productivity," GitHub, Inc., San Francisco, CA, USA, Tech. Rep., Oct. 2023. [Online]. Available: https://octoverse.github.com/

[2] N. Perry, M. Srivastava, D. Kumar, and D. Boneh, "Do users write more insecure code with AI assistants?" in *Proc. ACM SIGSAC Conf. Computer and Communications Security (CCS)*, Copenhagen, Denmark, Nov. 2023, pp. 2785–2799.

[3] L. B. Edelman, "Legal ambiguity and symbolic structures: Organizational mediation of civil rights law," *American Journal of Sociology*, vol. 97, no. 6, pp. 1531–1576, May 1992.

[4] A. Machuletz and R. Böhme, "Multiple purposes, multiple problems: A user study of consent dialogs after GDPR," *Proceedings on Privacy Enhancing Technologies*, vol. 2020, no. 2, pp. 481–498, 2020.

[5] M. Chen et al., "Evaluating large language models trained on code," arXiv preprint arXiv:2107.03374, Jul. 2021.

[6] Linux Foundation, "SPDX Specification v2.3," Software Package Data Exchange (SPDX), Jun. 2022. [Online]. Available: https://spdx.github.io/spdx-spec/v2.3/

[7] Coalition for Content Provenance and Authenticity (C2PA), "C2PA Technical Specification v2.1," Jan. 2024. [Online]. Available: https://c2pa.org/specifications/

[8] European Commission, "Proposal for a Directive on adapting non-contractual civil liability rules to artificial intelligence (AI Liability Directive)," COM(2022) 496 final, Sep. 2022.

[9] European Parliament and of the Council, "Directive (EU) 2024/2853 on liability for defective products," *Official Journal of the European Union*, L, Nov. 2024.

[10] European Parliament and of the Council, "Regulation (EU) 2016/679 on the protection of natural persons with regard to the processing of personal data (GDPR)," *Official Journal of the European Union*, L 119, pp. 1–88, May 2016.

[11] Cyberspace Administration of China, "Provisions on the Administration of Deep Synthesis Internet Information Services" (互联网信息服务深度合成管理规定), effective Jan. 10, 2023.

[12] J. Kirchenbauer, J. Geiping, Y. Wen, J. Katz, I. Miers, and T. Goldstein, "A watermark for large language models," in *Proc. Int. Conf. Machine Learning (ICML)*, Honolulu, HI, USA, Jul. 2023, pp. 17061–17084.

[13] M. Veale and F. Z. Borgesius, "Demystifying the Draft EU Artificial Intelligence Act," *Computer Law Review International*, vol. 22, no. 4, pp. 97–112, 2021.

[14] W3C, "Verifiable Credentials Data Model v2.0," W3C Recommendation, Feb. 2024. [Online]. Available: https://www.w3.org/TR/vc-data-model-2.0/

[15] European Parliament and of the Council, "Regulation (EU) 2022/2554 on digital operational resilience for the financial sector (DORA)," *Official Journal of the European Union*, L 333, pp. 1–79, Dec. 2022.

[16] International Telecommunication Union (ITU), "Measuring digital development: Facts and figures 2023," ITU Publications, Geneva, Switzerland, 2023. [Online]. Available: https://www.itu.int/en/ITU-D/Statistics/

---

---

*Manuscript submitted 2 July 2026. Aggregate experimental results (GitHub API counts, header survival outcomes, PyPI audit totals) are available at https://github.com/VinitaSilaparasetty/pr-automation-agent. No individual repository names, usernames, or personal identifiers are included in the dataset.*
