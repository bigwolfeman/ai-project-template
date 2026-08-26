# Campaign: Tiny generic-command fixture

Status: ready

Self-contained fixture for integration tests. Not a live campaign.

## Research question

[docs/experiments/planned/2026-08-24-tiny-generic-fixture.md](../../../../docs/experiments/planned/2026-08-24-tiny-generic-fixture.md)

This program does not copy predictions.

## Goal

Prove the local runner can validate, baseline, and trial a tiny subject against a sealed evaluator.

## Non-goals

Do not promote fixture output into `src/`.

## Mutable surface

Files under `subject/` may change between trials.

## Protected resources

`eval/`, `evaluator.lock.json`, and `campaign.yaml` are protected.

## Budget and stop

`max_trial_count` is 3. Stop on stagnation or consecutive crashes as declared in `campaign.yaml`.
