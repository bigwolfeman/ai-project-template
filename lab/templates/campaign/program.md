# Campaign: Example generic-command campaign

Status: draft

This file is a copyable template. Copy it into `lab/campaigns/<slug>/`. Do not run research from `lab/templates/campaign/`.

## Research question

The planned experiment owns the question, hypothesis, and predictions:

[lab/experiments/planned/2026-08-24-example-generic-command.md](../../../lab/experiments/planned/2026-08-24-example-generic-command.md)

This program must not copy those predictions. After copy into a live campaign, replace this example link if the campaign uses a different planned experiment.

## Goal

The operator wants a generic command evaluator that checks a mutable subject against sealed tests and a latency measurement.

## Non-goals

The agent must not promote output into `src/` from this template.
The agent must not treat this directory as a live campaign.

## Mutable surface

The agent may change files under `subject/` after the operator copies this template into a live campaign.

## Protected resources

The evaluator command, fixtures, and lock file listed in `campaign.yaml` are protected. The runner verifies `evaluator.lock.json` before and after each trial.

## Budget and stop

The manifest sets a wall-clock limit, a trial-count limit, and a stagnation limit. The agent stops when any of those limits fire.
