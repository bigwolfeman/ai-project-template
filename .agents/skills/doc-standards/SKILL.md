---
name: doc-standards
description: Use when writing, moving, or auditing documentation — choosing where a fact lives, trimming duplicated rules, or responding to verify_template.py failures.
---

# Documentation standards

Rules live in [docs/AGENTS.md](../../../docs/AGENTS.md). Experiments: [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md). Notes: [.agents/notes/README.md](../../notes/README.md).

## Authoring order

1. Locate the document in the tree and name its subject.
2. Keep full detail only about that subject; link children.
3. Tutorial vs reference: pick one. Split if both are substantial.
4. Grep distinctive phrases so the same rule is not copied.

## What goes where

- Standing order → root `AGENTS.md` plus a link
- Project vision / long-term principles → `docs/constitution.md` (fill the template with the user; do not leave it as shipped)
- Why we chose X → Agent Note
- How to do X → `docs/cookbook/`
- Measured claim → experiment
- Bug that escaped → postmortem

## Validate

`python scripts/verify_template.py`
