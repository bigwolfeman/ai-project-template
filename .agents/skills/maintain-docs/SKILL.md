---
name: maintain-docs
description: >-
  Places documentation in the correct home, trims duplicated rules, validates
  with verify_template.py, and archives or supersedes Agent Notes. Use when
  writing, moving, or auditing docs; when adding, auditing, archiving, or
  deleting Agent Notes; or when verify_template.py fails on layout.
---

# Maintain documentation and Agent Notes

Rules for placement live in [docs/AGENTS.md](../../../docs/AGENTS.md). Experiments: [lab/experiments/AGENTS.md](../../../lab/experiments/AGENTS.md). Lab: [lab/AGENTS.md](../../../lab/AGENTS.md). Notes: [.agents/notes/README.md](../../notes/README.md) and [.agents/notes/archived/AGENTS.md](../../notes/archived/AGENTS.md).

Apply ASD-STE100 principles when revising prose. The STE checklist lives in [../research-shared/references/ste100-style.md](../research-shared/references/ste100-style.md). Do not claim official conformance.

## One home per fact

1. Locate the document in the tree and name its subject.
2. Keep full detail only about that subject; link children.
3. Tutorial vs reference: pick one. Split if both are substantial.
4. Grep distinctive phrases so the same rule is not copied.
5. Follow the instruction-style standing order in root `AGENTS.md`.

### What goes where

- Standing order → root `AGENTS.md` plus a link
- Project vision / long-term principles → `docs/constitution.md` (fill the template with the user; do not leave it as shipped)
- Why we chose X → Agent Note under `.agents/notes/`
- How to do X → `.agents/cookbook/`
- Measured claim → experiment under `lab/experiments/`
- Informal exploration → `lab/spikes/`
- Bounded research program → `lab/campaigns/` plus experiment files
- Bug that escaped → `.agents/postmortem/`

A spike is not an experiment. An experiment is not a campaign. A trial outcome is not a hypothesis verdict.

## Agent Notes — add, supersede, archive

### When adding a note

Search `.agents/notes/proposed`, `implemented`, and `rejected` for the same decision. Archive fully superseded implemented notes in the same change. Cross-link partial supersessions. Reject obsolete proposals. Delete rejected notes that no longer prevent a real mistake.

### Classify implemented notes

Keep active when rationale, alternatives, negative guarantees, ownership, security, or reintroduction conditions still guide work.

Archive when the decision is complete and the body is unlikely to guide future work (one-off chrome, closed minor bugs, process history now obvious elsewhere).

Never archive a proposed note. Reject it instead.

### Archive steps

1. Move `implemented/{class}/yyyy-mm-dd-slug.md` to `archived/{class}/yyyy-mm-dd-slug.md`.
2. Insert `Archived: YYYY-MM-DD` immediately under `Status: implemented`. No other body edits.
3. Repair inbound links from active docs.
4. Run the verifier below.

## Validate

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

A failed command is an error. The agent must not treat a failure as a hint.
