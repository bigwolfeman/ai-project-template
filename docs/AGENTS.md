# AGENTS.md — Documentation standard

Placement, document kinds, and slop. Agent Notes stay outside this file's structural pass; they follow [.agents/notes/README.md](../.agents/notes/README.md). Experiments follow [experiments/AGENTS.md](experiments/AGENTS.md).

## Document kinds

Classify every human-facing doc as **tutorial** or **reference**. Tutorials are ordered paths to an outcome. References define current behavior for lookup. Do not mix substantial tutorial and reference content in one file.

A document describes its own subject. Children are named by purpose only; link to the child for detail.

## The tier taxonomy: one home per fact

| Tier | Job | Does not belong there |
|---|---|---|
| Root `AGENTS.md` | Standing orders, 1–3 lines, link to home | Stories, procedures, examples |
| Subtree `AGENTS.md` | Orders for that subtree only | Rules already at root |
| `docs/constitution.md` | Principles that force layout | Per-file how-tos |
| Agent Notes | Why, what was given up, verification | Run logs, incident timelines |
| `docs/experiments/` | Hypothesis, predictions, method, results, updated belief | Architecture decisions |
| `docs/experiments/algorithms/` | Algorithm writeups and notebooks | Experiment run records |
| `docs/postmortem/` | Incident: what broke, why nets missed, guardrails | Design alternatives |
| `docs/cookbook/` | Numbered how-tos | Rationale (link the Agent Note) |
| Package or `src/` README | Contract of that code | JSDoc restatement |

Placement: bugs that escaped → postmortems; rationale → Agent Notes; procedures → cookbooks; measured inquiry → experiments; standing orders → root `AGENTS.md`.

## Writing rules

- Document current state, not change history, in reference docs.
- One idea per paragraph. Prefer links over restatement.
- Comments state contracts (failure, timing, ownership), not reasoning transcripts.
- Hunt slop: the same rule in two homes; "previously/now"; status annotations that rot; invented alternatives; emphasis on every sentence.

## Cross-references

Link with relative Markdown paths, never bare filenames or note numbers.
