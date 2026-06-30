## Summary

<!-- What does this PR add or change? -->

## EU AI Act — AI Disclosure (Art. 50 / Art. 52)

Was any part of this contribution generated or substantially assisted by an AI system?

- [ ] **No** — entirely human-authored
- [ ] **Yes** — AI-assisted (complete the fields below)

If yes:
- **AI system used**: <!-- e.g. GitHub Copilot, Claude, GPT-4 -->
- **What the AI generated**: <!-- e.g. asset function body, tests, docstrings -->
- **Human review performed**: <!-- describe what you verified manually -->

> Disclosing AI assistance is required under EU AI Act Art. 50 for systems deployed
> in the EU. See [compliance/AI_TRANSPARENCY_NOTICE.md](../compliance/AI_TRANSPARENCY_NOTICE.md).

---

## Checklist

- [ ] Follows path + naming rules in `.github/copilot-instructions.md`
- [ ] New asset registered in `defs_sandbox.py`
- [ ] `dagster asset list -m warehouse.oso_dagster.assets.ingest.defs_sandbox` passes locally
- [ ] Public demo assets still materialize (`fetch_jsonplaceholder_posts`, `fetch_countries_countries`)
- [ ] AI-generated files include the Art. 52 header comment
