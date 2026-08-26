# Bounded trial loop phase

The agent executes bounded research cycles against a sealed evaluator and a sealed baseline.

## Preconditions

Baseline verdict is `ready`. Evaluator lock matches disk. Stop conditions are numeric or named. The agent refuses `NEVER STOP` and any unbounded loop.

A runner exists that can create Git worktrees under `ignored/research/<slug>/worktrees/` and append the ledger. If no runner exists, the agent stops with `runner_required`. The agent does not mutate the operator working tree as a substitute.

## Steps

1. The agent reads current best, open issues, prior interventions, remaining budget, and stop conditions.
2. The agent checks stop conditions before the next candidate. If a declared condition already holds, the agent stops. The agent does not ask whether to continue.
3. The agent verifies the evaluator lock. Digest mismatch aborts the campaign.
4. The agent registers one focused hypothesis or issue intervention. A new falsifiable claim requires [run-experiment](../../run-experiment/SKILL.md) first. This loop does not write Predictions.
5. The runner creates one isolated candidate from the current best, an approved exploratory parent, or a declared archive candidate. The parent identifier is recorded. Isolation is a worktree, not the operator working branch. When applicable: `scripts/run_campaign.py trial <campaign-dir> --candidate-id <id>`.
6. The agent mutates only included paths inside that worktree. The agent does not run `git reset --hard` to discard a candidate. Rejected work keeps an immutable identifier.
7. The runner runs the evaluator with the declared timeout and environment.
8. On complete evaluator output, the agent follows [evaluate.md](evaluate.md).
9. On crash, invalid packaging, or digest alarm, the agent follows [diagnose.md](diagnose.md).
10. The runner appends the trial outcome. Outcomes are `accepted`, `rejected`, `invalid`, `inconclusive`, or `crashed`. Those words are not hypothesis verdicts.
11. If the comparator accepts the candidate under campaign policy, the runner advances the named best reference. The runner does not rewrite history.
12. The agent may update issues per [issues.md](issues.md). The agent does not embed a second full procedure in the ledger.
13. The agent returns to step 1 without asking “Should I continue?”
14. When a stop condition fires, the agent writes `reports/loop-stop.md`.

Crashed or invalid trials consume budget. The agent does not ignore them.

Optional status: `scripts/run_campaign.py status <campaign-dir>`.

## Loop-stop output

```text
# Loop stop
Campaign: <slug>
Stop condition: <type from campaign.yaml>
Trials this session:
Remaining budget:
Best candidate identifier:
Last trial outcome: accepted | rejected | invalid | inconclusive | crashed
Continuation: stop
Operator approval required: yes | no
```

## State transitions

Via the runner: `ready` → `running` at first post-baseline trial; `running` → `stopped` on a declared stop; `running` → `completed` on `goal_met`; `running` → `paused` when the contract requires operator input; `running` → `aborted` on integrity, safety, or unrecoverable budget failure.

## Refusals

Unbounded loops. `NEVER STOP`. Per-trial “Should I continue?” prompts. `git reset --hard`. Mutation of undeclared paths without operator approval. Hand-written ledger events during an automated run.
