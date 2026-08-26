# Few-shot examples — baseline-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: tokenizer campaign harness is stable

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm` is `ready`. Operator accepted the evaluator. `evaluator.lock.json` digests match `data/holdout/val.bin`, `eval/bpb.py`, and `tests/eval/`.

Unchanged subject commit: `a1b2c3d4`. Replication: seeds 1, 2, 3. Equivalence margin on bits per byte: 0.02. Trial timeout: 7200 s.

Operator: establish the baseline, then start mutation.

A runner exists.

### Decision summary

- Do not mutate tokenizer or model code.
- Verify lock digests before the run.
- Run the unchanged commit three times. Record mean and stddev.
- Confirm artifacts and timeout.
- If stddev is small relative to 0.02 and constraints pass, seal the baseline and permit mutation.
- Runner appends ledger and reconstructs projections. Agent does not hand-write ledger rows.

### Actions

1. The agent confirms state `ready` and a clean mutable/protected tree.
2. The agent verifies lock digests.
3. The runner isolates commit `a1b2c3d4` in a worktree.
4. The evaluator runs seeds 1, 2, 3 within 7200 s. Hard constraints pass.
5. The agent confirms artifact digests for logs and metric files.
6. The runner reconstructs `state/baseline.json` from the ledger.
7. The agent writes `reports/baseline.md` with verdict `ready`.

### Output

```text
# Baseline report
Campaign: tok-arch-lm
Candidate identifier: a1b2c3d4
Replication: n=3, seeds=[1,2,3], mean_stddev
Measurements:
- bpb: mean 1.140, stddev 0.006, n=3
Hard-constraint results: all pass
Timeout result: within limit
Artifact capture: complete
Ledger reconstruction: matched
Variance vs equivalence margin: 0.006 < 0.02, stable
Verdict: ready
Mutation: permitted
```

`state/baseline.json`: `sealed: true`, `candidate_id: a1b2c3d4`. `state/best.json` `source: baseline`.

### Stop behavior

The agent stops. Mutation has not started. Handoff: `run-research-loop`. The agent does not ask to skip the baseline. The agent does not use `git reset --hard`.

## Example 2 — Failure / boundary: unstable variance, mutation refused

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Same campaign `tok-arch-lm`. Lock digests match.

Baseline repeats: bits per byte 1.11, 1.19, 1.08. stddev = 0.056. Equivalence margin = 0.02. `min_repeats` = 3. `single_noisy_run_advances_baseline` = false.

Operator after the numbers:

> Seed 2 looked good enough. Seal it and start mutating. We can fix variance later.

### Decision summary

- The harness ran. Artifacts exist. This is not an integrity abort.
- stddev 0.056 is larger than margin 0.02. Comparisons cannot discriminate candidates. The baseline is unstable.
- A single lucky seed must not seal the baseline.
- Verdict `blocked`. Mutation refused.
- Do not rewrite the margin to make the baseline look stable.

### Actions

1. The agent records the three measurements and stddev.
2. The agent compares stddev to the equivalence margin.
3. The agent writes verdict `blocked` and `Mutation: refused`.
4. The agent refuses the operator request to seal from one seed.
5. The agent does not start `run-research-loop`.
6. The runner does not append a successful `baseline_completed` seal. Campaign state stays `ready`.

### Output

```text
# Baseline report
Campaign: tok-arch-lm
Candidate identifier: a1b2c3d4
Replication: n=3, seeds=[1,2,3], mean_stddev
Measurements:
- bpb: mean 1.127, stddev 0.056, n=3
Hard-constraint results: all pass
Timeout result: within limit
Artifact capture: complete
Ledger reconstruction: matched
Variance vs equivalence margin: 0.056 > 0.02, unstable
Verdict: blocked
Mutation: refused
error: unstable_baseline
refused: seal from one seed; start mutation before a stable baseline
```

### Stop behavior

The agent stops with `blocked`. The agent does not mutate. The operator must change replication, timeout, or the harness. Fail loud.

## Example 3 — Different domain: physics solver conservation harness

**Domain:** physics simulation

**Kind:** different domain

### Input

Campaign `nbody-energy`. Subject: unchanged symplectic integrator. Protected: analytic energy residual, holdout ICs, evaluator. Mutable: integrator source (not touched in this skill).

Hard constraint: energy residual ≤ 1e-8 on the holdout ICs. Replication: 5 repeats (threading jitter). Timeout: 120 s. Operator approved the baseline launch. Runner exists.

### Decision summary

- Baseline is the unchanged integrator, not a “better” candidate.
- Conservation is a hard constraint. If the unchanged subject fails it, the harness is blocked. Do not start mutation to “fix” a broken evaluator.
- Measure residual mean and stddev. Confirm artifacts (trajectory digest) and timeout.
- Trial outcome language does not apply to hypothesis truth. This skill writes ready or blocked only.

### Actions

1. The agent verifies lock digests for residual code and holdout ICs.
2. The runner runs the unchanged integrator five times.
3. The evaluator records energy residual and wall time.
4. The agent confirms trajectory artifacts and timeout.
5. The agent writes `reports/baseline.md`.

### Output

```text
# Baseline report
Campaign: nbody-energy
Candidate identifier: 9f00aa11
Replication: n=5, mean_stddev
Measurements:
- energy_residual: mean 2.1e-9, stddev 4.0e-10, n=5
- wall_s: mean 14.2, stddev 0.3, n=5
Hard-constraint results: energy_residual <= 1e-8 pass
Timeout result: within limit (120 s)
Artifact capture: complete
Ledger reconstruction: matched
Variance vs equivalence margin: residual stddev below margin, stable
Verdict: ready
Mutation: permitted
```

### Stop behavior

The agent stops and hands off to `run-research-loop`. The agent does not edit integrator source. The agent does not promote into `src/`. If residual had failed on the unchanged subject, the agent would block and refuse mutation.
