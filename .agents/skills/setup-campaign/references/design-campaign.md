# Phase 2 — Design campaign files

The agent creates the operational campaign definition under `lab/campaigns/<slug>/`. The agent does not run trials. The agent does not hand-write ledger events as if a runner executed.

## Preconditions

- Work is classified as campaign (or bug-investigation that needs a campaign).
- `lab/templates/campaign/` exists with at least `program.md` and `campaign.yaml`.
- A scope draft exists, or the operator supplies the same facts in this session.
- Material cost is approved when cost is not zero.
- `lab/campaigns/<slug>/` does not already exist (unless the operator asks to revise).

If the template is missing, the agent stops. The agent reports the missing path. The agent does not invent a live campaign from memory.

## Required inputs

- Campaign slug (lowercase, hyphenated)
- Research question (does not assert an answer)
- Mutable paths
- Protected paths
- Resource budget with at least one total limit and one stagnation limit
- Stop conditions
- Isolation choice (this slice: Git worktrees and a restricted subprocess, not containers)
- Exploration mode: greedy ratchet or bounded branch exploration

## Copy and fill

1. Confirm the work is a campaign. If spike or single experiment, stop and hand off.
2. Verify the template directory exists.
3. Verify the destination does not exist.
4. Copy `lab/templates/campaign/` to `lab/campaigns/<slug>/`. Do not edit the template in place.
5. Fill `campaign.yaml`. Keep every field the template requires. Do not add unknown fields.
6. Set mutable paths and protected paths as disjoint sets.
7. Set isolation to Git worktrees under `ignored/research/<slug>/worktrees/` unless the operator names a different approved model.
8. Set exploration policy. Greedy ratchet is the default. Select bounded branch exploration only when a one-step comparison cannot test the claim.
9. Write `program.md`: intent, non-goals, budgets, stop conditions. Link planned experiment documents. Do not copy hypotheses or Predictions.
10. Write `reports/evaluator-design-request.md`. Do not seal `evaluator.lock.json`.
11. Ask the operator to review budget, protected paths, and mutable paths.
12. Leave `state/` as draft projections from the template. Do not append fake trial events to `state/ledger.jsonl`.
13. Do not mark the campaign `ready`. State remains `draft` until the operator approves budget, protected resources, and the evaluator.

## `campaign.yaml` must define

Using the template’s field names:

- schema version and campaign identifier
- title and research-question links
- mutable paths and protected paths
- evaluator command and evaluator lock path
- environment command
- measurement schema reference
- hard constraints, comparator policy, replication policy, complexity policy
- branch and worktree policy
- exploration policy
- resource budget and stop conditions
- artifact policy, network policy, secret policy, promotion policy

## `program.md` must contain

- goal and non-goals
- links to `docs/experiments/planned/` files, or a statement that none exist yet and a pointer to [run-experiment](../../run-experiment/SKILL.md)
- budget summary (limits, not a copy of experiment predictions)
- `## Evaluator design request` or a link to `reports/evaluator-design-request.md`

If the operator asks to paste `## Predictions` into `program.md`, the agent refuses. Experiments own predictions. The program links them.

## Refusals

- Unbounded run without numeric limits
- Pasting Predictions into `program.md`
- Synthesizing a campaign layout when the template is missing
- `git reset --hard` as a reject mechanism (no candidate exists yet; the rule still stands)
- Promoting into `src/` from this phase
