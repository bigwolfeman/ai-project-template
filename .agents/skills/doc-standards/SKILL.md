---
name: doc-standards
description: Use when writing, moving, or auditing documentation — choosing where a fact lives, trimming duplicated rules, or responding to verify_template.py failures.
---

# Documentation standards

Rules live in [docs/AGENTS.md](../../../docs/AGENTS.md). Experiments: [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md). Lab: [lab/AGENTS.md](../../../lab/AGENTS.md). Notes: [.agents/notes/README.md](../../notes/README.md).

## Authoring order

1. Locate the document in the tree and name its subject.
2. Keep full detail only about that subject; link children.
3. Tutorial vs reference: pick one. Split if both are substantial.
4. Grep distinctive phrases so the same rule is not copied.
5. Follow the instruction-style standing order in root AGENTS.md. Do not claim official ASD-STE100 conformance.

## What goes where

- Standing order → root `AGENTS.md` plus a link
- Project vision / long-term principles → `docs/constitution.md` (fill the template with the user; do not leave it as shipped)
- Why we chose X → Agent Note
- How to do X → `docs/cookbook/`
- Measured claim → experiment under `docs/experiments/`
- Informal exploration → `lab/spikes/`
- Bounded research program → `lab/campaigns/` plus experiment files; how-to: [docs/cookbook/starting-a-campaign.md](../../../docs/cookbook/starting-a-campaign.md)
- Bug that escaped → postmortem

A spike is not an experiment. An experiment is not a campaign. A trial outcome is not a hypothesis verdict.

## Validate

`python scripts/verify_template.py`
