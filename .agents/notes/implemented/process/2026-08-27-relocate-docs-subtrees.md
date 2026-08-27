# Agent Note: Relocate cookbook, experiments, postmortem

Status: implemented

## Problem

Cookbook, experiments, and postmortem lived under `docs/` while `docs/` was meant to hold project vision (`constitution.md`) and documentation placement rules. Experiments are research evidence (lab plane). Cookbook and postmortem are agent/operator workflow artifacts (`.agents` plane).

## Decision

| Former path | New path |
|---|---|
| `docs/experiments/` | `lab/experiments/` |
| `docs/cookbook/` | `.agents/cookbook/` |
| `docs/postmortem/` | `.agents/postmortem/` |

`docs/` keeps `constitution.md` and `AGENTS.md` only. Update verifiers, cursor rules, skills, cookbooks, lab templates, and standing orders.

## Alternatives considered

- **All under `.agents/`** — rejected; experiments pair with spikes and campaigns in `lab/`.
- **All under `lab/`** — rejected; cookbooks and postmortems are not execution artifacts.

## Consequences

- Every link to `docs/experiments/`, `docs/cookbook/`, or `docs/postmortem/` must use the new paths.
- `scripts/verify_template.py` validates `lab/experiments/` and requires `.agents/cookbook/README.md` and `.agents/postmortem/README.md`.
- Verification: `python scripts/verify_template.py` and `python -m unittest discover -s tests -q`.
