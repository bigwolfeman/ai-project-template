# Mining notes: DeepSeek Harness → this template

Source: https://github.com/deepseek-ai/deepseek-harness (sparse clone in `ignored/`, not committed).

## What we kept as architecture

- Root `AGENTS.md` as standing orders with short bullets and links to owning docs
- `CLAUDE.md` as a pointer to `AGENTS.md`
- Nested `AGENTS.md` in `docs/` and `.agents/notes/`
- Agent Notes as path-encoded RFC/ADRs: `{lifecycle}/{class}/yyyy-mm-dd-slug.md`
- Lifecycles: proposed, implemented, rejected, archived (frozen)
- Classes: feature, bug-fix, simplification, architecture, process, testing
- Mandatory alternatives considered
- Implemented notes stay present-tense and current with shipped facts
- Doc tiers / one home per fact
- Postmortems vs notes vs cookbooks
- Skills as reusable workflows, not product contracts

## What we did not copy

- Cordis/plugin product layout, packages/, i18n triplets, generated catalogs, doc word-count gates, TypeScript verify scripts
- Verbatim AGENTS.md prose (copyright; too product-specific)

## What we added

- `docs/experiments/{algorithms,planned,successes,failures,results}`
- Predictions-before-results, enforced by `scripts/verify_template.py`
- Constitution principle for scientific method
- Cursor rules for standing orders, notes, and experiments
