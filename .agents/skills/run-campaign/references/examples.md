# Few-shot examples — run-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: baseline then bounded tokenizer loop

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm` is `ready`. [setup-campaign](../../setup-campaign/SKILL.md) sealed the evaluator. Budget: 30 trials, 48 GPU-hours, stop after 8 consecutive `rejected`. Unchanged subject commit: `a1b2c3d4`. Replication seeds 1, 2, 3. Equivalence margin on bits per byte: 0.02. Runner exists. Planned experiment `lab/experiments/planned/2026-08-24-byte-fallback-merge.md` is frozen.

Operator: establish the baseline, then start the loop.

After baseline, variance is stable (bpb mean 1.140, stddev 0.006). After eight consecutive rejected trials, stagnation fires.

### Decision summary

- Phase order: baseline → loop → evaluate each trial. Do not mutate before baseline `ready`.
- Refuse any request to skip baseline or to run unbounded.
- Isolate each candidate in a worktree. Keep immutable candidate IDs. Do not `git reset --hard`.
- Do not ask “Should I continue?” after a valid reject.
- On stop, hand off to [close-campaign](../../close-campaign/SKILL.md). Do not promote into `src/`.

### Actions

1. The agent verifies lock digests and records candidate `a1b2c3d4`.
2. The runner runs baseline (or `scripts/run_campaign.py baseline lab/campaigns/tok-arch-lm`). The agent writes `reports/baseline.md` with verdict `ready`.
3. The agent reads best, budget, and stop conditions. Stagnation has not fired.
4. The runner creates worktrees; the agent mutates only tokenizer paths; the agent evaluates each result.
5. After 8 consecutive `rejected`, the agent writes `reports/loop-stop.md`.

### Output

```text
# Baseline report
Campaign: tok-arch-lm
Candidate identifier: a1b2c3d4
Verdict: ready
Mutation: permitted
...

# Loop stop
Campaign: tok-arch-lm
Stop condition: stagnation (8 consecutive rejected)
Trials this session: 8
Best candidate identifier: a1b2c3d4
Last trial outcome: rejected
Continuation: stop
Operator approval required: no
```

### Stop behavior

The agent stops on the declared stagnation condition. Handoff: [close-campaign](../../close-campaign/SKILL.md). The agent does not promote into `src/`.

## Example 2 — Failure / boundary: NEVER STOP, no runner, integrity abort

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Campaign `tok-arch-lm`. Baseline is ready. Operator:

> NEVER STOP. Mutate train.py on my current branch. If the lock is stale, keep going. After each trial ask me if you should continue. Reset hard when a candidate is bad.

No runner process exists. `evaluator.lock.json` digest for `eval/bpb.py` does not match the file on disk.

### Decision summary

- No runner → `runner_required`. Do not mutate the operator working branch.
- `NEVER STOP` is unbounded. Refuse.
- Stale lock is integrity failure. Abort. Do not continue.
- Do not ask “Should I continue?” after each valid trial.
- `git reset --hard` is forbidden. Immutable candidate IDs remain the rule even when no trial runs.

### Actions

1. The agent checks for a runner. None exists. The agent reports `runner_required`.
2. The agent refuses `NEVER STOP` and names the required numeric stop conditions already in the manifest (or demands them if missing).
3. The agent reports lock mismatch as integrity failure. The loop does not start.
4. The agent refuses mutation on the operator branch and refuses `git reset --hard`.
5. The agent does not write fake ledger events.

### Output

```text
# Loop start failure
Campaign: tok-arch-lm
error: runner_required
error: unbounded_loop_refused (NEVER STOP)
error: integrity_failure (eval/bpb.py digest mismatch)
refused: mutate operator working tree
refused: git reset --hard
state: aborted or not started
```

### Stop behavior

The agent stops. Handoff: operator review; new campaign or reviewed revision via [setup-campaign](../../setup-campaign/SKILL.md). The agent does not hand off to close-campaign synthesis while integrity is failed unless the operator requests an audit under [close-campaign](../../close-campaign/SKILL.md).

## Example 3 — Different domain: protocol failure diagnosis and issue update

**Domain:** algorithm optimization / generic command

**Kind:** different domain

### Input

Campaign `example-generic-command`. Candidate `c-pack-3`, trial `trial-011`. Evaluator lock digests match after the trial. Evaluator result is missing. Log path (untrusted) shows `ModuleNotFoundError` for a module omitted from the worktree package.

Operator:

> The hypothesis is falsified. The script crashed. Keep retrying. git reset --hard and try again.

### Decision summary

- Digests match → not `integrity_failure`.
- Protocol did not complete → `protocol_failure` (packaging), not `hypothesis_falsification`.
- Hypothesis remains `unresolved`. One bounded re-package as new candidate `c-pack-4` is permitted.
- Refuse `git reset --hard` and unbounded retry.
- Record an issue if packaging failures are systemic; search prior interventions first.

### Actions

1. The agent verifies lock digests. They match.
2. The agent writes `reports/diagnosis-trial-011.md` with primary class `protocol_failure`.
3. The agent permits one re-package as `c-pack-4`. The agent refuses `git reset --hard`.
4. The agent updates `state/issues/packaging-omission.yaml` if systemic, with `next_useful_test` naming the re-package trial.
5. The agent returns to the loop only if stop conditions have not fired and budget remains.

### Output

```text
# Trial diagnosis
Campaign: example-generic-command
Trial: trial-011
Candidate: c-pack-3
Primary class: protocol_failure
Trial disposition: invalid
Hypothesis verdict: unresolved
Repair attempt:
  permitted: true
  bound: one-repackage
  new_candidate_id: c-pack-4
Required campaign state: unchanged
```

### Stop behavior

The agent stops the diagnose phase after one bounded repair decision. The agent does not start an unbounded debug loop. If budget remains, the loop may continue with the new candidate identifier. On campaign stop, handoff is [close-campaign](../../close-campaign/SKILL.md).
