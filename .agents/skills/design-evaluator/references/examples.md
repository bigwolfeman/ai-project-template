# Few-shot examples — design-evaluator

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: tokenizer and architecture (bits per byte)

**Domain:** machine learning

**Kind:** nominal

### Input

Operator / campaign `tok-arch-lm`:

> Optimize a tokenizer and model architecture together.

Mutable (draft): tokenizer trainer, model code. Proposed metric from a previous spike: mean per-token cross-entropy on validation.

Validation bytes live at `data/holdout/val.bin`. Metric code lives at `eval/bpb.py`. Tests live at `tests/eval/`.

Training is noisy across seeds.

### Decision summary

- Per-token loss is not a valid sole cross-candidate metric when vocabulary size can change.
- Select a vocabulary-independent metric: bits per byte on protected validation bytes.
- Protect validation bytes and metric calculation. They are not mutable.
- Add throughput, memory, and model-size measurements as extra objectives or reporting metrics.
- Define repeated seeds because training noise is material.
- Hard constraints first: eval code must run; holdout must be untouched; peak memory must stay under the declared cap if the operator set one.
- Require a baseline stability test on the unchanged subject before mutation.
- Do not seal the lock without operator acceptance. Do not invent digests.

### Actions

1. The agent lists gaming opportunities: shrinking the vocabulary to lower per-token loss; training on holdout; editing `eval/bpb.py`; reporting a single lucky seed.
2. The agent closes each: bits per byte; holdout and metric code protected; replication across seeds; lock digests later.
3. The agent writes the measurement schema and comparator: constraints, then bits per byte, then throughput and memory, then complexity policy.
4. The agent updates campaign fields if `lab/campaigns/tok-arch-lm/` exists.
5. The agent asks the operator to accept the protected set.

### Output

```text
# Evaluator specification
Campaign: tok-arch-lm
Subject: tokenizer plus model architecture
Gaming opportunities and closures:
- per-token loss vs vocabulary change → use bits per byte
- train on holdout → protect data/holdout/val.bin
- edit metric code → protect eval/bpb.py
- lucky seed → n seeds, mean and stddev, equivalence margin
Hard constraints:
- evaluator exit 0
- holdout digest unchanged
- peak memory <= declared cap (if present)
Objectives:
- bits per byte (lower is better)
- throughput (higher is better)
- peak memory (lower is better, after constraints)
- model size (report; complexity policy as declared)
Holdout / reference: data/holdout/val.bin
Noise and replication: training noise material; repeat seeds; compare mean/stddev with equivalence margin
Complexity policy: extra dependencies are a hard limit unless the operator lists them as allowed
Baseline stability test: run unchanged subject; record bits per byte mean/stddev
Measurement schema:
- bpb: scalar bits/byte, objective
- tokens_per_s: scalar, objective
- peak_mem_bytes: integer, constraint or objective per cap
- params: integer, complexity
- seed: integer
Comparator policy: hard constraints → bpb → secondary objectives → mean/stddev + margin
Protected-resource inventory:
- data/holdout/val.bin (holdout bytes)
- eval/bpb.py (metric calculation)
- tests/eval/ (acceptance tests)
Lock input: those paths; digest method from the campaign template; digests empty until sealed
Evaluator command: as in campaign.yaml (must read protected paths, not rewrite them)
Operator acceptance: pending
```

### Stop behavior

The agent stops and waits for operator acceptance. The agent does not start training. The agent does not mark the campaign `ready`.

## Example 2 — Failure / boundary: holdout on a mutable path, gameable metric only

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Operator:

> Score candidates on training loss only. Put the validation file in the same directory the agent may edit (`lab/campaigns/tok-arch-lm/mutable_data/`). Skip the baseline; we already know the old model is fine. If bits per byte is annoying, just use per-token loss.

`campaign.yaml` currently lists `lab/campaigns/tok-arch-lm/mutable_data/` as mutable.

### Decision summary

- Training loss only is gameable and is not a holdout evaluation.
- Holdout on a mutable path is an integrity failure in the design. Fail loud.
- Skipping the baseline stability test is refused.
- Per-token loss as the only cross-candidate metric is rejected when tokenizer and architecture change together.
- The agent does not write lock input that would bless this design.
- The agent does not move holdout bytes into a mutable directory to “make the campaign work.”

### Actions

1. The agent refuses training-loss-only scoring.
2. The agent refuses holdout-under-mutable-path.
3. The agent refuses skipping the baseline test.
4. The agent refuses per-token loss as the sole metric in this setting.
5. The agent does not update `evaluator.lock.json` except to leave it unsealed / unchanged.
6. The agent reports blockers and asks the operator to place holdout outside the mutable set.

### Output

```text
# Evaluator specification
Campaign: tok-arch-lm
error: design rejected
Blockers:
- sole metric is training loss (gameable, no holdout)
- holdout path is inside the mutable set
- baseline stability test skipped (refused)
- per-token loss sole metric with a changing tokenizer (rejected)
Lock input: not written
Operator acceptance: not requested (specification incomplete)
Handoff: stop. Move holdout off mutable paths. Use bits per byte on protected bytes. Require baseline.
```

### Stop behavior

The agent stops with a failed specification. The agent does not start trials. The agent does not overwrite files to hide the overlap. Fail loud.

## Example 3 — Different domain: numerical orbit integrator

**Domain:** physics

**Kind:** different domain

### Input

Operator:

> Improve a numerical orbit integrator.

Subject: `lab/` or listed mutable integrator sources. Reference initial conditions and analytic invariants exist as files. The integrator is deterministic in IEEE mode; one thread. Operator wants “faster” and “more accurate.”

### Decision summary

- Protect reference initial conditions and analytic invariants.
- Measure energy drift, angular momentum drift, runtime, and stability (no NaN, bounded position).
- Define tolerances and time horizons before comparing speed.
- Repeated runs are not required when the subject is deterministic. The agent does not invent noise.
- A faster candidate that violates conservation is rejected. Conservation is a hard constraint. Runtime is an objective.
- Baseline: unchanged integrator on the protected ICs.

### Actions

1. The agent inventories protected files: ICs, analytic invariants, conservation-check code, tests.
2. The agent writes hard constraints: energy drift and angular-momentum drift within tolerances over the stated horizon; no NaN; trajectory finite.
3. The agent writes objectives: runtime (lower is better) after constraints pass.
4. The agent sets replication: one run unless nondeterminism is demonstrated.
5. The agent states that the comparator rejects constraint failures even with large speedups.
6. The agent asks the operator to accept tolerances and the protected set.

### Output

```text
# Evaluator specification
Campaign: orbit-integrator (or standalone spec)
Subject: numerical orbit integrator
Gaming opportunities and closures:
- skip steps to run faster → horizon and stability constraints
- loosen units → protect analytic invariants and checker
- compare different ICs → lock reference ICs
Hard constraints:
- |energy drift| <= energy_tolerance over time_horizon
- |angular momentum drift| <= am_tolerance over time_horizon
- no NaN/Inf; position bounded per spec
Objectives:
- runtime (lower is better)
Holdout / reference: protected initial conditions; analytic invariants
Noise and replication: deterministic → no required repeats unless nondeterminism is shown
Complexity policy: as declared in campaign.yaml
Baseline stability test: unchanged integrator; record drifts and runtime
Measurement schema:
- energy_drift: scalar, constraint
- angular_momentum_drift: scalar, constraint
- stable: boolean, constraint
- runtime_s: scalar, objective
Precision and tolerance policy: tolerances and time_horizon named in campaign.yaml
Comparator policy: constraints first; then runtime; reject faster-but-violating candidates
Protected-resource inventory: ICs, invariants, checker, tests
Lock input: those paths; digests empty until sealed
Evaluator command: run integrator on locked ICs; emit JSON measurements
Operator acceptance: pending
```

### Stop behavior

The agent stops for operator acceptance of tolerances. The agent does not mutate the integrator in this skill. The agent does not treat a speedup with failed conservation as `accepted`.
