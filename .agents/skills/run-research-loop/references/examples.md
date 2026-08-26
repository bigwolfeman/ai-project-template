# Few-shot examples — run-research-loop

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: bounded tokenizer loop, no per-trial continue prompt

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm`. Baseline sealed, verdict `ready`. Budget: 30 trials, 48 GPU-hours, stop after 8 consecutive `rejected`. Runner exists. Best = baseline `a1b2c3d4`.

Planned experiment `docs/experiments/planned/2026-08-24-byte-fallback-merge.md` is frozen. Remaining budget: 30 trials.

Operator: start the loop.

After trial 3 the comparator returns `rejected`. After trial 8 consecutive rejects, stagnation fires. No operator message is required between trials.

### Decision summary

- Runner required. Isolate each candidate in a worktree from current best.
- One hypothesis per cycle. Do not write Predictions in the loop.
- Delegate classification to `evaluate-candidate`.
- Do not ask “Should I continue?” after a valid reject.
- Stop when 8 consecutive rejected trials fire the declared stagnation condition.
- Keep rejected commit identifiers. Do not run `git reset --hard`.

### Actions

1. The agent reads best, budget, and stop conditions. Stagnation has not fired.
2. The agent registers the frozen planned hypothesis as `testing`.
3. The runner creates a worktree from `a1b2c3d4` and a new candidate commit.
4. The agent mutates only tokenizer paths listed in the manifest.
5. The runner runs the evaluator. The agent calls `evaluate-candidate`.
6. Trial outcome `rejected`. The runner appends the ledger. Best stays `a1b2c3d4`.
7. The agent starts the next cycle without asking the operator.
8. After 8 consecutive `rejected`, the agent writes `reports/loop-stop.md`.

### Output

```text
# Loop stop
Campaign: tok-arch-lm
Stop condition: stagnation (8 consecutive rejected)
Trials this session: 8
Remaining budget: 22 trials, GPU-hours remaining per ledger
Best candidate identifier: a1b2c3d4
Last trial outcome: rejected
Continuation: stop
Operator approval required: no
```

Rejected candidates retain commit identifiers in the ledger.

### Stop behavior

The agent stops on the declared stagnation condition. The agent does not ask to continue. Handoff: later synthesis. The agent does not promote into `src/`.

## Example 2 — Failure / boundary: no runner, NEVER STOP, integrity abort

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Campaign `tok-arch-lm`. Baseline is ready. Operator:

> NEVER STOP. Mutate train.py on my current branch. If the lock is stale, keep going. After each trial ask me if you should continue. Reset hard when a candidate is bad.

No runner process exists. `evaluator.lock.json` digest for `eval/bpb.py` does not match the file on disk.

### Decision summary

- No runner: report `runner_required`. Do not mutate the operator working branch.
- `NEVER STOP` is unbounded. Refuse. Named stop conditions already exist in the manifest; the agent uses those, or stops until the operator names numeric limits.
- Stale lock is integrity failure. Abort. Do not continue.
- Do not ask “Should I continue?” after each valid trial. That question is forbidden even when a runner exists.
- `git reset --hard` is forbidden.

### Actions

1. The agent checks for a runner. None exists. The agent reports `runner_required`.
2. The agent refuses `NEVER STOP`.
3. The agent reports lock mismatch as integrity failure. Campaign aborts if a run had started; here the loop does not start.
4. The agent refuses mutation on the operator branch.
5. The agent refuses `git reset --hard`.
6. The agent does not write fake ledger events.

### Output

```text
# Loop start failure
Campaign: tok-arch-lm
error: runner_required
error: unbounded_loop_refused
error: evaluator_lock_mismatch
refused: mutate operator working branch
refused: git reset --hard
refused: ask Should I continue after each trial
created_paths: none
state_transition: none (would be aborted if a run were in progress)
```

### Stop behavior

The agent stops. Fail loud. The operator must supply a runner, repair the lock, and keep declared stop conditions. The agent does not return `aborted` to `running`.

## Example 3 — Different domain: deadlock campaign, consecutive inconclusive

**Domain:** bug investigation

**Kind:** different domain

### Input

Campaign `worker-deadlock`. Baseline ready: stress harness on unchanged pool, timeout 180 s, reproduction is noisy. Stop after 6 consecutive `inconclusive` trials. Budget 40 trials. Runner exists.

Current best = baseline. Open issue: `lock-order` vs `missed-wakeup` (records exist as pointers; `manage-research-issues` is not this skill).

Hypothesis file for lock-order is planned and frozen. First three trials: stress does not deadlock (`inconclusive`, not a fix). Fourth through sixth: same.

Operator is silent during the loop.

### Decision summary

- A clean stress run is `inconclusive`, not `accepted`, and not hypothesis `supported`.
- Do not ask the operator to continue after each inconclusive trial.
- Stop at 6 consecutive `inconclusive` as declared.
- Keep candidate commits. Do not reset Git to hide failed reproductions.
- Do not merge to `src/`.

### Actions

1. The agent reads stop conditions: 6 consecutive inconclusive.
2. The runner isolates a candidate that changes lock order in listed mutable paths.
3. The evaluator runs stress. No deadlock this trial. `evaluate-candidate` returns `inconclusive`.
4. The agent continues without a continue prompt.
5. After 6 consecutive `inconclusive`, the agent stops and writes `reports/loop-stop.md`.

### Output

```text
# Loop stop
Campaign: worker-deadlock
Stop condition: stagnation (6 consecutive inconclusive)
Trials this session: 6
Remaining budget: 34 trials
Best candidate identifier: <baseline commit>
Last trial outcome: inconclusive
Continuation: stop
Operator approval required: no
Note: inconclusive is a trial outcome, not hypothesis supported
```

### Stop behavior

The agent stops on the declared condition. The agent does not call a non-reproducing run a fix. The agent does not start an unbounded “keep trying until it deadlocks” loop.
