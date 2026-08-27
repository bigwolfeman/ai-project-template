# Experiment: Generic command evaluator latency and pass rate

Status: planned

Date proposed: 2026-08-24
Algorithm: none — standard method
Owner: template maintainers

## Question

Does a sealed generic-command evaluator on an unchanged subject report a stable pass rate and a latency distribution that the campaign can use as a baseline before any mutation?

## Hypothesis

On the template subject and sealed fixtures, three consecutive baseline runs of the generic-command evaluator each report all hard constraints passed, and the mean wall-clock latency across those three runs differs by at most 20% from the first run's mean latency under the same host load class.

## Predictions

Write these before any run. Commit this file while it still lives in `planned/` with no Results section.

If the hypothesis is true, we will observe:

- Each of three baseline runs exits with evaluator status that marks every hard constraint as passed.
- Mean latency for run 2 and run 3 each lie within ±20% of run 1's mean latency.
- The evaluator lock digest is unchanged across the three runs.

If the hypothesis is false, we will observe:

- At least one hard constraint fails on an unchanged subject, or
- Mean latency for run 2 or run 3 differs from run 1 by more than 20%, or
- The evaluator lock digest changes between runs.

What would make this run inconclusive (protocol failure, not a hypothesis test):

- The campaign runner CLI or evaluator command is missing and cannot be executed.
- Host load changes class between runs (documented thermal throttle, competing jobs, or power-profile change).
- The subject or fixtures were mutated before baseline completed.

## Method

1. Copy `lab/templates/campaign/` to a disposable campaign under `lab/campaigns/` only if a live campaign is required. For template verification, treat this file as the linked example for the generic-command program theme.
2. Confirm `evaluator.lock.json` matches protected resources. Do not mutate protected paths.
3. Run the sealed evaluator three times on the unchanged subject with the same command and environment scrub (`env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH`).
4. Record pass/fail of hard constraints, mean latency, lock digest, and host load notes under `lab/experiments/results/2026-08-24-example-generic-command/` (or the matching campaign artifact pointer).
5. Compare runs against the predictions above. Do not edit Predictions after artifacts exist.
6. Stop when three runs are recorded or when a protocol failure makes the hypothesis untestable.

Campaign link after copy: `lab/campaigns/<slug>/program.md` must point at this file. Do not copy these predictions into `program.md`.

## Related

- Campaign template: [lab/templates/campaign/program.md](../../../lab/templates/campaign/program.md)
- Architecture: [.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md](../../../.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md)
- Cookbook: [.agents/cookbook/running-a-campaign.md](../../../.agents/cookbook/running-a-campaign.md)
