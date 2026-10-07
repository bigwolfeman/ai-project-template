# Experiment: Tiny generic-command fixture

Status: planned

Date proposed: 2026-08-24
Algorithm: none — standard method
Owner: template fixture

## Question

Can a sealed generic-command evaluator report tests_passed and latency_ms for a tiny mutable subject under a fixed wall-clock budget?

## Hypothesis

When subject/work.py exposes LATENCY_MS and eval/run.py is sealed, the evaluator returns tests_passed true and a numeric latency_ms that the comparator can compare across candidates.

## Predictions

If the hypothesis is true, we will observe:

- evaluator_status success
- tests_passed true
- latency_ms within the declared valid range

If the result is mixed, we will observe:

- tests_passed true and latency_ms present, but outside the declared valid range on one of the two trials

If the hypothesis is false (a solid dead end), we will observe:

- tests_passed false, or
- missing latency_ms, or
- evaluator_status error, timeout, or crash

What would make this run inconclusive (protocol failure, not a hypothesis test):

- protected digests change during the trial
- the fixture cannot start because the campaign directory is not a Git worktree when isolation requires one

## Method

```
copy tests/fixtures/campaigns/tiny-generic -> temporary git repo
seal evaluator.lock.json digests
run scripts/run_campaign.py validate
run scripts/run_campaign.py baseline
edit subject/work.py: change LATENCY_MS
run scripts/run_campaign.py trial
compare: evaluator_status, tests_passed, latency_ms, lock digest
```

Copy tests/fixtures/campaigns/tiny-generic into a temporary Git repository. Seal evaluator.lock.json digests. Run scripts/run_campaign.py validate, baseline, then trial after changing LATENCY_MS. Do not edit Predictions after artifacts exist.

## Related

- lab/templates/campaign/
- .agents/skills/run-campaign/SKILL.md
