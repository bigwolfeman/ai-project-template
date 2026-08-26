# Phase 3 — Design evaluator and lock input

The agent builds an invariant and auditable evaluation contract. The agent separates holdout data from mutable data. The agent places hard constraints before objectives.

The agent does not run the evaluator as a trial loop. The agent does not declare the lock sealed without operator acceptance.

## Required inputs

- Campaign identifier, or a standalone spec name
- Subject under test
- Hard constraints (correctness, conservation, safety)
- Objectives (latency, loss, throughput) ranked after constraints
- Holdout or reference data identity
- Noise source, if any (training seeds, threading, measurement jitter)
- Complexity policy (hard limit, lexicographic tie-break, weighted objective, or human-review item)

## Design steps

1. Name the claim the evaluator must discriminate. Name what the evaluator must not reward.
2. List metric-gaming opportunities. Close each with a constraint, a holdout, or a rejected metric.
3. Separate mutable paths from protected paths. Fail loud if they overlap.
4. Define hard constraints first. A candidate that fails a hard constraint is rejected even if objectives improve.
5. Define objectives and comparator order: hard constraints, then declared objectives, then mean and standard deviation with an equivalence margin.
6. Define noise and replication. Require repeated seeds when training or measurement noise is material. Do not require repeats when the subject is deterministic.
7. Define complexity treatment. Complexity is an explicit hard limit, a lexicographic tie-break, a weighted objective, or a human-review item. Do not ignore added dependencies or large line-count growth.
8. Require a baseline stability test: run the unchanged subject before mutation. Record that requirement. This skill does not execute the baseline; [run-campaign](../../run-campaign/SKILL.md) does.
9. Select tests as the default evidence. Select Z3 or Lean only when they are cheaper and sufficient for a stated property. See [formal-methods.md](../../research-shared/references/formal-methods.md).
10. Write the measurement schema, comparator policy, protected-resource inventory, and lock input.
11. Ask the operator to accept the protected set and the evaluator command.

## Metric rules

Cross-candidate metrics must be comparable. Per-token loss is not a valid sole metric when vocabulary size changes. Prefer a vocabulary-independent metric such as bits per byte when that situation applies.

Prompt tests, when used, are deterministic rule checks.

Every measurement names its unit, direction of improvement, and whether it is a constraint or an objective.

## Lock input

The lock input lists protected paths and the digest method.

A digest field may be empty until the operator seals the lock. The agent does not invent digests.

File permissions are not the integrity check. The runner verifies digests before and after each trial when a runner exists.

## Authorized updates when a campaign exists

- `campaign.yaml` fields for evaluator command, measurement schema, hard constraints, comparator policy, replication policy, and complexity policy
- `reports/` evaluator specification
- `evaluator.lock.json` as lock *input* only

The agent does not set campaign state to `ready`. The agent does not append ledger events. The agent does not change `src/`.

## Measurement schema types

Allowed types: scalar, integer count, boolean constraint, categorical verdict, confidence interval, sample distribution, structured proof result.

## Refusals

- Sole metric that is gameable or not comparable across candidates
- Holdout data on a mutable path
- Skip of the baseline stability test
- Overwriting a lock to hide a digest mismatch
- Sealing without operator acceptance
- Starting an autonomous trial loop from this phase
