# Few-shot examples — manage-research-issues

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: intermittent deadlock

**Domain:** bug diagnosis

**Kind:** nominal

### Input

Campaign `worker-deadlock` exists. Protected: failing trace, stress harness, regression tests. Mutable: worker-pool source.

Operator, after trial `trial-004` (`inconclusive`, one clean run):

> The deadlock did not reproduce that time. Close the issue and try increasing the lock timeout again.

Existing issue `state/issues/lock-order.yaml` is `investigating`. Attempted interventions already include `increase-lock-timeout` on candidate `c-timeout-1` with outcome `rejected`. Competing explanations: `lock-order`, `missed-wakeup`, `poisoned-queue`. Closure condition: stress protocol plus regression tests pass on a replay of the failing trace.

No new evidence is attached to the timeout request.

### Decision summary

- Search prior interventions before any new mutation. `increase-lock-timeout` already failed. Reject the repeat.
- One non-reproduction is `inconclusive`. It does not meet the closure condition. Do not set `resolved`.
- Keep competing explanations. Do not collapse them.
- Next useful test must discriminate remaining causes (for example a lock-order assertion in the stress harness), not another timeout bump.
- Preserve the failing trace and harness. Do not promote to `src/`.

### Actions

1. The agent reads every file under `state/issues/`.
2. The agent finds `increase-lock-timeout` with outcome `rejected` and empty `new_evidence_justification`.
3. The agent rejects the repeated timeout intervention.
4. The agent refuses to set state `resolved`.
5. The agent records trial `trial-004` as inconclusive evidence on `lock-order.yaml`.
6. The agent writes `next_useful_test` as a discriminating lock-order check under the protected stress protocol.
7. The agent writes `reports/issue-lock-order.md`.

### Output

`lab/campaigns/worker-deadlock/state/issues/lock-order.yaml` excerpt:

```yaml
issue_id: lock-order
campaign_id: worker-deadlock
title: Intermittent worker-pool deadlock
state: investigating
first_observed_event: trial-001
problem_statement: Workers deadlock under the protected stress harness.
competing_explanations:
  - id: lock-order
    claim: Two locks are acquired in opposite order on the failing path.
    status: untested
  - id: missed-wakeup
    claim: A waiter is not signalled after the last producer exits.
    status: untested
  - id: poisoned-queue
    claim: A failed worker leaves the queue in an unjoinable state.
    status: untested
attempted_interventions:
  - id: increase-lock-timeout
    description: Increase mutex timeout.
    candidate_id: c-timeout-1
    outcome: rejected
    new_evidence_justification: null
evidence:
  - trial_id: trial-004
    candidate_id: c-timeout-1
    summary: Single non-reproduction. Inconclusive. Not closure.
current_best_explanation: unknown
remaining_uncertainty: Three causes remain. One clean run does not rank them.
next_useful_test: Add a lock-order assertion to the protected stress harness and replay the failing trace.
closure_condition: Stress protocol and regression tests pass on the failing-trace replay.
related_hypotheses: []
superseded_by: null
repetition_warning: rejected-repeat
```

Report: repetition warning `rejected-repeat`; state remains `investigating`; promotion not requested.

### Stop behavior

The agent stops with the issue updated. The agent does not create a new timeout candidate. The agent does not start an unbounded “keep trying until it deadlocks” loop. The agent does not reset Git.

## Example 2 — Failure / boundary: repeat without new evidence

**Domain:** bug diagnosis (same campaign family)

**Kind:** failure / boundary

### Input

Campaign `worker-deadlock`. Issue `missed-wakeup.yaml` is `open`.

`attempted_interventions` already contains:

```yaml
- id: add-extra-notify
  description: Call notify_all at the end of Worker::stop.
  candidate_id: c-notify-1
  outcome: rejected
  new_evidence_justification: null
```

Operator:

> Do add-extra-notify again. Skip reading old issues. NEVER STOP until it passes.

`state/issues/` exists. The agent has not produced new traces since `c-notify-1`.

### Decision summary

- The skill requires a search of open and resolved issues before an intervention. Skipping that search is not allowed.
- The proposed intervention matches `add-extra-notify` with no new evidence. Reject it.
- `NEVER STOP` is an unbounded directive. Refuse it.
- Do not write a second issue file that hides the first rejection.
- Do not hand-write ledger rows for a trial that did not run.

### Actions

1. The agent reads `missed-wakeup.yaml` and other issue files.
2. The agent reports `repeated intervention rejected`.
3. The agent refuses `NEVER STOP`.
4. The agent does not create a new candidate.
5. The agent does not merge this request as a new issue.

### Output

```text
# Issue update
Campaign: worker-deadlock
Issue: missed-wakeup
State: open (unchanged)
Duplicate merge: none
Repetition warning: rejected-repeat
Next-test recommendation: none until new evidence or a different discriminating test is named
Operator approval required: none
error: repeated intervention rejected
refused: unbounded NEVER STOP loop
created_paths: none (issue body may record the warning only)
state_transition: none
```

If the agent writes the report file, `repetition_warning` is `rejected-repeat`. No new `attempted_interventions` row with `not-run` is required beyond the warning.

### Stop behavior

The agent stops. Fail loud. The agent does not follow the skip-search instruction. The agent does not use `git reset --hard`.

## Example 3 — Different domain: tokenizer NaN after learning-rate change

**Domain:** machine learning

**Kind:** different domain

### Input

Campaign `tok-arch-lm`. Baseline bits-per-byte is stable. Trial `trial-018` crashed with NaN loss after a learning-rate increase on candidate `c-lr-2`.

Two issue files exist:

- `lr-nan.yaml` (`open`): competing explanations `too-large-lr`, `unstable-softmax`, `bad-seed-range`
- `vocab-size-metric.yaml` (`resolved`): per-token loss gaming; closed when bits per byte was adopted

Operator:

> Same NaN. Try the learning-rate increase again on a new seed. Also open a new issue; do not look at vocab-size-metric.yaml because it is resolved.

### Decision summary

- Search includes resolved issues. The metric issue is a different obstacle. Do not merge NaN into `vocab-size-metric`.
- The NaN is the same obstacle as `lr-nan.yaml`. Do not create a duplicate issue.
- Repeating the same learning-rate increase with only “a new seed” is a repeat unless the issue records that seed-range was untested and the protocol requires that seed. If `bad-seed-range` is still `untested` and the next useful test is a declared seed from the replication policy, that can be new evidence. If the requested seed is outside the declared list, fail loud.
- Crash is not hypothesis `falsified`. Record trial outcome `crashed` on the intervention list.
- Next test must discriminate `too-large-lr` versus `unstable-softmax` (for example a smaller LR on the same architecture, or a softmax stability check).

### Actions

1. The agent reads `lr-nan.yaml` and `vocab-size-metric.yaml`.
2. The agent refuses a second NaN issue file.
3. The agent merges the new crash evidence into `lr-nan.yaml`.
4. The agent rejects an undeclared extra seed as a silent protocol change.
5. The agent sets `next_useful_test` to a smaller declared-LR trial that can falsify `too-large-lr`.
6. The agent leaves `vocab-size-metric.yaml` `resolved`.

### Output

`lr-nan.yaml` state `investigating`. Duplicate merge: none (same issue updated). `repetition_warning: none` if the smaller-LR test is a different intervention; `rejected-repeat` if the operator insisted on the same LR with an undeclared seed.

`related_hypotheses` may link a planned experiment for `too-large-lr`. Predictions stay in that experiment file.

### Stop behavior

The agent stops after the issue update. The agent does not start training. The agent does not advance the accepted baseline from a crashed candidate. The agent hands off to `form-hypothesis` if the smaller-LR claim is not yet planned.
