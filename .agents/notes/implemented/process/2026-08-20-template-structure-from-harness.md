# Agent Note: Template structure mined from DeepSeek Harness plus scientific experiments

Status: implemented

## Problem

New AI-assisted repositories dump decisions, spikes, run logs, and production code into ad-hoc markdown. Agents cannot tell what is shipped, what was decided, what was measured, or what is still a guess. DeepSeek Harness showed a workable layout for agent instructions and notes, but it has no first-class scientific-method experiment tree.

## Decision

This repository is a starter template, not a harness fork. It copies the *information architecture*:

- Root `AGENTS.md` holds standing orders (one to three lines) and links to owning docs. `CLAUDE.md` points at the same file.
- Subtree `AGENTS.md` files hold only local rules.
- Agent Notes live at `.agents/notes/{lifecycle}/{class}/yyyy-mm-dd-slug.md` with mandatory Problem / decision-or-proposal / Alternatives considered.
- Documentation kinds stay split: cookbooks for procedures, postmortems for escaped incidents, constitution for the project's own vision (the shipped `docs/constitution.md` is a fill-in template; root `AGENTS.md` requires writing it with the user at project start and rereading it every context window).

It adds `lab/experiments/` with `algorithms/`, `planned/`, `successes/`, `failures/`, and `results/`. Predictions are committed in `planned/` before any run. `scripts/verify_template.py` rejects planned files that contain Results, completed files missing Verdict or Updated hypothesis, and notes whose Status disagrees with their folder.

Bilingual pairing, generated catalogs, and DeepSeek-specific gates are not part of this template.

## Alternatives considered

- **Copy deepseek-harness wholesale** — inherits plugin/Cordis product structure that new projects do not need, plus copyrighted standing orders that are too specific to dsh.
- **ADRs only under `docs/adr/`** — familiar, but does not encode proposed/implemented/rejected in the path and does not force alternatives-considered.
- **Experiments as a notebook directory with no planned stage** — agents write the story after the plot, which is the failure mode this template exists to block.
- **Keep experiments only as Agent Notes** — conflates design rationale with empirical runs; a failed training curve is not a rejected RFC.

## Consequences

- New projects start with empty class folders and copy templates rather than inventing layout.
- Agents must run `python scripts/verify_template.py` after note or experiment edits.
- Consumers still have to add language-specific tooling (`src/`, tests, CI); this template only enforces documentation and experiment hygiene.
