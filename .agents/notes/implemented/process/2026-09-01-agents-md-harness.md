# Agent Note: AGENTS.md harness files under .agents/

Status: implemented

## Problem

Subtree indexes under `.agents/` used `README.md`. The DeepSeek-style harness reads `AGENTS.md` at each tier, not README. Agents could miss cookbook, skills catalog, notes format, and postmortem rules unless another doc linked them.

## Decision

- Add top-level [.agents/AGENTS.md](../../../AGENTS.md) as glossary, plane map, classify-work guide, and subtree index.
- Replace `README.md` with `AGENTS.md` in `notes/`, `skills/`, `cookbook/`, and `postmortem/`.
- Merge former `notes/README.md` body into `notes/AGENTS.md` (single file).
- Require these paths in `scripts/verify_template.py` and point `verify_campaign.py` at `skills/AGENTS.md`.
- Update root `AGENTS.md`, standing orders, and inbound links.

## Alternatives considered

- **Keep README and duplicate into AGENTS.md** — rejected; one home per fact.
- **Glossary only in research-shared/terminology.md** — rejected; `.agents/` needs an entry the harness reads before subtree work.

## Consequences

- Links must use `.agents/*/AGENTS.md`, not `README.md`.
- Root standing orders require reading `.agents/AGENTS.md` when work touches the agent workspace.
- Verification: `python scripts/verify_template.py`.
