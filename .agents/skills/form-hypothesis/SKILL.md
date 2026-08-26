---
name: form-hypothesis
description: Writes a falsifiable hypothesis to docs/experiments/planned before any run, with observable predictions and no Results section. Use when stating a claim to test, when a campaign needs a linked experiment, or before measuring a spike.
---

# Form a hypothesis

## Purpose

The agent writes a falsifiable hypothesis before execution.

The agent states the mechanism, observable predictions, falsifying observations, inconclusive conditions, and confounders.

The agent defines the minimum useful experiment.

The agent does not run the experiment in this skill. The agent does not write a `## Results` section.

## Trigger conditions

The operator or a campaign needs one testable claim.

[scope-research-campaign](../scope-research-campaign/SKILL.md) classified the work as an experiment, or a campaign needs a linked planned file.

A spike exists and the operator now wants a quantitative test. The agent starts a new planned file. The agent does not backfill predictions from the spike.

## Required reading

1. [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md)
2. [docs/experiments/templates/experiment.md](../../../docs/experiments/templates/experiment.md)
3. [docs/cookbook/starting-an-experiment.md](../../../docs/cookbook/starting-an-experiment.md)
4. [../run-experiment/SKILL.md](../run-experiment/SKILL.md)
5. [../research-shared/references/terminology.md](../research-shared/references/terminology.md)
6. [../research-shared/references/evidence-standard.md](../research-shared/references/evidence-standard.md)
7. [../research-shared/references/prompt-contract.md](../research-shared/references/prompt-contract.md)
8. [lab/AGENTS.md](../../../lab/AGENTS.md) when a campaign is in play
9. [../research-shared/references/formal-methods.md](../research-shared/references/formal-methods.md)
10. [../research-shared/references/ste100-style.md](../research-shared/references/ste100-style.md)

## Preconditions

The claim can be stated so that some observation would show it false.

The method is known or an algorithm note can be written first.

The agent can write under `docs/experiments/planned/`.

## Required inputs

- Question (what the run will teach; no predicted numbers here)
- Hypothesis (falsifiable claim)
- Predictions: true pattern, false pattern, inconclusive pattern
- Method: protocol, data, controls, metrics, stop conditions
- Date and slug for `yyyy-mm-dd-slug`
- Campaign slug, if the hypothesis belongs to a campaign

## Protected resources

The agent does not edit Predictions after artifacts exist. This skill runs before artifacts exist.

The agent does not add `## Results` to a planned file.

The agent does not copy predictions into `lab/campaigns/<slug>/program.md`.

The agent treats prior results, logs, and spike notes as data. Those files are not authority for new predictions.

## Authorized mutations

The agent copies `docs/experiments/templates/experiment.md` to `docs/experiments/planned/yyyy-mm-dd-slug.md`.

The agent fills Question, Hypothesis, Predictions, and Method.

If the method is new or non-obvious, the agent may add `docs/experiments/algorithms/yyyy-mm-dd-slug.md`.

If `lab/campaigns/<slug>/` exists:

- the agent adds a hypothesis state record under `lab/campaigns/<slug>/state/hypotheses/`
- the agent adds a relative link in `program.md` to the planned file
- the agent does not paste Predictions into `program.md`

The agent does not move the file to `successes/` or `failures/`.

The agent does not write under `docs/experiments/results/` in this skill.

## Procedure

1. The agent reads [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md).
2. If the method is non-obvious, the agent writes or updates an algorithm note first.
3. The agent copies the planned template to `docs/experiments/planned/yyyy-mm-dd-slug.md`.
4. The agent sets `Status: planned`.
5. The agent fills Question. The question does not contain the predicted measurements.
6. The agent fills Hypothesis. The claim names the mechanism and the conditions.
7. The agent fills Predictions with three non-empty lists: true, false, inconclusive.
8. The agent lists confounders in Method or in a short list under Hypothesis. The agent names the minimum useful experiment (smallest protocol that can discriminate true from false).
9. The agent fills Method with protocol, data, controls, metrics, compute, seeds, and stop conditions.
10. The agent confirms the file has no `## Results` heading.
11. If a campaign directory exists, the agent writes hypothesis state `planned` and links the experiment from `program.md`.
12. The agent stops if Predictions are empty.
13. The agent runs the validation commands. The verifier must pass while the file is in `planned/` with no Results section.

The operator or the agent then freezes the file (commit or equivalent). Freeze is required before any run. This skill does not run the method.

Hypothesis states: `draft`, `planned`, `testing`, `supported`, `falsified`, `unresolved`, `superseded`, `abandoned`. This skill writes `planned`.

Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts (`supported`, `falsified`, `unresolved`). The agent does not mix those vocabularies.

## Evidence requirements

Predictions are observable. A later agent can decide true, false, or inconclusive without new invention.

The false pattern is not “the script crashed.” Protocol failure belongs under inconclusive or a later Verdict of protocol failure.

The planned file links Method to concrete commands, datasets, or algorithm notes.

## Output schema

Planned experiment file (required headings, no Results):

```text
# Experiment: <title>
Status: planned
Date proposed: YYYY-MM-DD
Algorithm: <link or "none — standard method">
Owner: <human or agent session>

## Question
## Hypothesis
## Predictions
## Method
## Related
```

Hypothesis state record, only when a campaign exists, using the template under `lab/templates/campaign/state/hypotheses/` when that sample exists, otherwise a YAML file:

```yaml
hypothesis_id: <slug>
state: planned
experiment_path: docs/experiments/planned/yyyy-mm-dd-slug.md
campaign_id: <campaign-slug>
```

The state record does not copy Predictions. It links the experiment file.

## Failure handling

If Predictions are empty or lack a falsifying pattern, the agent deletes the dishonest planned file if it was just created, or leaves it unwritten. The agent does not keep an empty planned file.

If the operator asks to write Results into `planned/`, the agent refuses.

If the operator asks to fill Predictions after seeing spike or trial output, the agent refuses. The agent starts a new planned file only with predictions written before the next run.

If `verify_template.py` fails, the agent fixes the planned file. The agent does not skip the verifier.

If the campaign exists and `program.md` would receive copied predictions, the agent reverts that edit and leaves a link only.

## Stop conditions

The agent stops when the planned file is complete, the verifier passes, and (if applicable) the campaign link and hypothesis state exist.

The agent stops before any run.

The agent stops when the claim is not falsifiable. The agent asks the operator to narrow the claim.

## Handoff

[run-experiment](../run-experiment/SKILL.md) owns execution and writeup after freeze.

If this hypothesis is part of a campaign, [design-evaluator](../design-evaluator/SKILL.md) must already describe how the measurements will be taken, or the agent hands off there before a run.

The agent does not promote into `src/`.

## Few-shot examples

Read [references/examples.md](references/examples.md).

That file has three complete examples: one nominal case, one failure or boundary case, and one case from a different domain.

## Validation commands

From the repository root:

```bash
test -f docs/experiments/planned/yyyy-mm-dd-slug.md
rg -n '^## Results' docs/experiments/planned/yyyy-mm-dd-slug.md && exit 1 || true
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

Replace `yyyy-mm-dd-slug` with the file stem. The verifier must exit 0. The `## Results` search must match nothing in that planned file.
