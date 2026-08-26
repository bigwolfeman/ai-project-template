# Baseline phase

The agent validates the complete research harness before mutation begins.

## Preconditions

Campaign state is `ready`. Mutation has not started. The evaluator lock is sealed. Digests match disk.

The subject on mutable paths is the unchanged candidate the operator intends as baseline.

Protected or mutable paths are clean of unrecorded operator edits. If they are dirty, the agent stops.

## Steps

1. The agent confirms campaign state is `ready` and that no trial has mutated the subject.
2. The agent verifies every digest in `evaluator.lock.json`. Mismatch → integrity failure → abort.
3. The agent records the unchanged candidate identifier (Git commit or content digest). The agent does not run `git reset --hard`.
4. The runner creates an isolated worktree from that commit. The runner does not mutate the operator working branch. When applicable: `scripts/run_campaign.py baseline <campaign-dir>`. If no runner exists, the agent launches `evaluator_command` only with operator approval, and only on the unchanged subject.
5. The runner applies the declared trial timeout. Timeout of the unchanged subject → baseline `blocked`.
6. The evaluator runs the declared protocol, including repeats required by `replication_policy`.
7. The agent checks artifact capture. Missing required artifacts → `blocked`.
8. The agent measures variance. If noise is material and `n` is below `min_repeats`, baseline is `blocked`.
9. The agent compares measured standard deviation to the equivalence margin. Unstable → `blocked`; mutation refused.
10. The runner appends `baseline_started` / `baseline_completed` when a runner exists and reconstructs projections. Reconstruction mismatch → fail loud.
11. The agent writes `reports/baseline.md`.

A single favorable noisy run must not seal the baseline unless `single_noisy_run_advances_baseline` is true.

## Output

```text
# Baseline report
Campaign: <slug>
Candidate identifier:
Evaluator digest:
Protocol digest:
Environment digest:
Replication: n, seeds, confidence method
Measurements: name, value, unit, stddev, n
Hard-constraint results:
Timeout result: within limit | timed out
Artifact capture: complete | missing <paths>
Ledger reconstruction: matched | mismatched | runner_absent
Variance vs equivalence margin:
Verdict: ready | blocked
Mutation: permitted | refused
```

On `ready`, `state/baseline.json` has `sealed: true` and a non-null `candidate_id`. `state/best.json` `source` is `baseline`.

On `blocked`, campaign state stays `ready`. Mutation does not start.

## Refusals

The agent refuses to skip the baseline. The agent refuses to mutate first and baseline later. The agent refuses an unstable baseline as “good enough.”
