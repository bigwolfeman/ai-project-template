# Project Constitution

**Version**: 1.0.0
**Ratified**: 2026-08-20
**Last Amended**: 2026-08-20

## Context and applicability

This repository is a **greenfield template** for AI-assisted projects. Clone it, then replace this preamble's project-specific sentences. The structure is the product: agents should be unable to dump notes, experiments, and production code into one pile.

**When these rules apply**

- All new code and documentation
- Promotion from `lab/` or `docs/experiments/` into production
- Significant refactors

**When override is permitted**

- Explicit user authorization with a one-line rationale in the change
- True emergency fixes (record the debt in `Incomplete/` the same day)

**Agent guidance**: when uncertain, follow the constitution.

## Principle 1: Lifecycle separation

**The rule**: Production code lives in `src/`. Unstructured spikes live in `lab/`. Measured inquiry lives in `docs/experiments/`. Decisions live in `.agents/notes/`. Incidents live in `docs/postmortem/`.

**Why**: Agents duplicate work when they cannot tell what is shipped, guessed, measured, or decided.

**How to apply**

- A spike with no hypothesis goes in `lab/` and dies or graduates; it does not become an experiment after the fact.
- An experiment starts in `docs/experiments/planned/` with predictions committed first.
- Promoting code to `src/` requires tests or an explicit Agent Note explaining why tests are not applicable.

## Principle 2: One home per fact

**The rule**: Each fact has one owning document. Other documents link; they do not copy.

**Why**: Duplicated rules drift. Agents follow the nearest copy.

**How to apply**: follow the tier table in [docs/AGENTS.md](AGENTS.md).

## Principle 3: Scientific method for experiments

**The rule**: Write the question, hypothesis, predictions, and method before any run. Results never appear in `planned/`. After the run, move the file to `successes/` or `failures/` and update the hypothesis from evidence. Inconclusive runs stay classified as failure of the *protocol* unless the hypothesis was actually tested.

**Why**: Post-hoc stories feel like science and are not.

**How to apply**: [docs/experiments/AGENTS.md](experiments/AGENTS.md).

## Principle 4: Decisions record what they beat

**The rule**: Every Agent Note states the problem, the decision or proposal, and the alternatives that lost.

**Why**: A decision without losers will be re-litigated.

**How to apply**: [.agents/notes/README.md](../.agents/notes/README.md).

## Principle 5: Fail loud

**The rule**: Missing files, failed commands, and invalid experiment state raise errors. No silent `except`, no skipped steps because "it should work".

**Validation**: `python scripts/verify_template.py` exits non-zero on layout or format violations.

## Directory structure

```
.
├── AGENTS.md
├── CLAUDE.md              # symlink → AGENTS.md
├── README.md
├── .agents/
│   ├── notes/
│   └── skills/
├── .cursor/rules/
├── docs/
│   ├── AGENTS.md
│   ├── constitution.md
│   ├── cookbook/
│   ├── experiments/
│   └── postmortem/
├── scripts/
│   └── verify_template.py
├── src/                   # create when code exists
└── lab/                   # optional spikes
```

## Governance

Amend by Agent Note in `.agents/notes/proposed/process/`, then update this file and bump:

- MAJOR: incompatible layout
- MINOR: new principle
- PATCH: clarification

Review when a pain point repeats twice.
