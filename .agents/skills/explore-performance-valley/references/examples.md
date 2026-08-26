# Few-shot examples — explore-performance-valley

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: data representation then algorithm

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm`. Original baseline candidate `c-base` in `state/baseline.json`. Accepted best is still `c-base`.

Operator:

> Changing the data representation regresses the first trial, but the new algorithm requires it.

Trial `trial-021` candidate `c-repr-1`: hard constraints pass; bits per byte regresses versus `c-base`. Exploration policy currently `greedy_ratchet`, `max_branch_depth: 1`.

Operator supplies: branch depth 2, branch budget 6 trials and 4 GPU-hours remaining inside the campaign budget, safety floor = existing hard constraints.

A planned experiment `docs/experiments/planned/2026-08-24-repr-plus-algorithm.md` already exists.

### Decision summary

- One-step evaluation is insufficient: the representation change is expected to regress until the matching algorithm lands.
- Do not advance the accepted baseline after this first-step regression. Best remains `c-base`.
- Depth 1 cannot test the valley. The plan needs depth 2 and operator approval to set `bounded_branch`.
- Intermediate objective regression is allowed. Hard-constraint failure would abandon the branch.
- Compare the final compound candidate to `c-base`, not to `c-repr-1`.
- Do not run trials in this skill. Recommendation stays `pending`.
- Do not `git reset --hard` to hide `c-repr-1`. Keep the identifier as the exploratory parent.

### Actions

1. The agent writes why greedy one-step comparison cannot test the compound claim.
2. The agent reads `c-base` from `baseline.json` and confirms `best.json` still names `c-base`.
3. The agent links the planned experiment. The agent does not copy Predictions.
4. The agent writes `reports/valley-repr-algo.md` with depth 2, the given budget, and safety floor = hard constraints.
5. The agent lists step 1 as representation (`c-repr-1`, `advance_best: false`) and step 2 as algorithm on that parent, compared to `c-base`.
6. The agent asks the operator to set `exploration_policy.mode` to `bounded_branch`.
7. The agent runs `verify_template.py`.

### Output

```text
# Valley exploration plan
Campaign: tok-arch-lm
Branch id: repr-algo
Why one-step evaluation is insufficient: the algorithm requires the new representation; the representation alone regresses bits per byte.
Compound hypothesis link: docs/experiments/planned/2026-08-24-repr-plus-algorithm.md
Original baseline candidate id: c-base
Accepted baseline remains: c-base
Parent candidate id: c-repr-1
Safety floor: campaign hard constraints (eval exit, holdout digest, memory cap)
Max branch depth: 2
Branch budget: 6 trials; 4 GPU-hours
Abandonment rules: budget exhausted; hard-constraint fail; 3 consecutive rejected compound results if campaign says so
Planned steps:
  - step: 1
    mutation: data representation
    parent: c-base
    expected intermediate comparison: may regress on bits per byte; must pass safety floor
    advance_best: false
  - step: 2
    mutation: algorithm that consumes the new representation
    parent: c-repr-1
    comparison_target: original baseline c-base
    advance_best: only if recommendation is merge
Recommendation: pending
Operator approval required: bounded_branch mode
```

`state/best.json` and `state/baseline.json` are unchanged.

### Stop behavior

The agent stops with the plan written. The agent does not start training. The agent does not adopt `c-repr-1` as best. The agent hands off to a future runner only after operator approval.

## Example 2 — Failure / boundary: advance best, reset Git, unbounded valley

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Same campaign. After `c-repr-1` regresses, operator:

> Make c-repr-1 the new baseline so the next step looks like a win. git reset --hard to drop the old tokenizer. Keep exploring the valley. NEVER STOP. Compare only to c-repr-1. Depth and budget unspecified.

`baseline.json` still names `c-base`.

### Decision summary

- Advancing best after the first-step regression is forbidden.
- Comparison target must be the original baseline `c-base`, not `c-repr-1`.
- `git reset --hard` is forbidden. `c-repr-1` keeps its identifier.
- Missing depth and budget: fail loud. Do not invent limits.
- `NEVER STOP` is refused.
- Do not rewrite `best.json` or `baseline.json`.
- Do not write a plan that blesses this request.

### Actions

1. The agent refuses to advance best to `c-repr-1`.
2. The agent refuses `git reset --hard`.
3. The agent refuses unbounded exploration.
4. The agent refuses comparison-only-to-intermediate.
5. The agent does not write `reports/valley-*.md` as complete, or writes a failure report with `error` and no `Recommendation: merge`.
6. The agent asks for depth ≥ 2 and a numeric branch budget.

### Output

```text
# Valley exploration plan
Campaign: tok-arch-lm
Branch id: not-created
error: valley refused
Blockers:
- advance accepted baseline after first-step regression (refused)
- compare compound candidate to intermediate c-repr-1 (refused)
- git reset --hard (refused)
- missing max_branch_depth and branch budget
- unbounded NEVER STOP (refused)
Accepted baseline remains: c-base
Recommendation: none
created_paths: none
state_transition: none
```

### Stop behavior

The agent stops. Fail loud. The agent does not mutate Git. The agent does not start a valley loop.

## Example 3 — Different domain: schema encoding then query plan

**Domain:** database query tuning

**Kind:** different domain

### Input

Campaign `orders-index-q`. Original baseline `c-sql-base` (mean latency 102 ms, hard constraint: result-set equality on the protected fixture).

Operator:

> Store order_date as epoch days. The first candidate is slower. The new query plan needs that encoding. Depth 2. Branch budget: 8 trials. Safety floor: result-set equality must hold on every intermediate.

Trial `trial-007` candidate `c-epoch-1`: equality holds; latency 140 ms (`regresses` vs `c-base` if compared now). Best is still `c-sql-base`.

No planned experiment exists yet.

### Decision summary

- This is a valley: encoding regresses until the planner rewrite exists.
- Do not advance best to `c-epoch-1`.
- Safety floor is the equality hard constraint. Intermediate latency regression is allowed.
- Final compound (encoding plus planner rewrite) must be compared to `c-sql-base`.
- Missing planned experiment: the plan can be drafted, but predictions must exist before any branch trial. Hand off to `form-hypothesis`.
- Do not treat noisy 0.3 ms differences as improvement later; that is comparator work. This skill only forbids advancing on the first regression.

### Actions

1. The agent writes the insufficiency statement (encoding is a required parent of the planner rewrite).
2. The agent keeps accepted baseline `c-sql-base`.
3. The agent writes `reports/valley-epoch-plan.md` with depth 2, 8-trial budget, safety floor = result-set equality.
4. The agent does not start the query runner.
5. The agent hands off to `form-hypothesis` for the compound claim.

### Output

Valley plan with `Recommendation: pending`, `Accepted baseline remains: c-sql-base`, step 1 `c-epoch-1` `advance_best: false`, step 2 planner rewrite compared to `c-sql-base`.

Handoff: `form-hypothesis` must write `docs/experiments/planned/` before trials.

### Stop behavior

The agent stops before trials. The agent does not promote SQL into `src/`. The agent does not reset Git to hide `c-epoch-1`. If the branch budget later expires without a dominating compound candidate, the recommendation becomes `abandon` from later evidence; this skill does not invent that result now.
