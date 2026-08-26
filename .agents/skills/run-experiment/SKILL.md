---
name: run-experiment
description: >-
  Forms a falsifiable hypothesis under docs/experiments/planned/ (Predictions
  before any run, no Results), runs the protocol, and writes up under
  successes/ or failures/. Use when proposing, running, or writing up an
  experiment, when a campaign needs a linked planned file, or before measuring
  a spike.
---

# Run an experiment

Read [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md) first. Do not start from `lab/spikes/` after the fact.

This skill covers one experiment file: form hypothesis → freeze → run → write up. A campaign that coordinates several experiments follows [.agents/skills/README.md](../README.md). Informal exploration stays in `lab/spikes/`. Classification of unclear work starts at [setup-campaign](../setup-campaign/SKILL.md).

## Form hypothesis (before any run)

The agent writes a falsifiable claim before execution. The agent does not run the method in this step. The agent does not write a `## Results` section into `planned/`.

1. Read [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md) and [docs/experiments/templates/experiment.md](../../../docs/experiments/templates/experiment.md).
2. If the method is non-obvious, add or update `docs/experiments/algorithms/yyyy-mm-dd-slug.md`.
3. Copy `docs/experiments/templates/experiment.md` to `docs/experiments/planned/yyyy-mm-dd-slug.md`.
4. Set `Status: planned`. Fill Question, Hypothesis, Predictions, Method.
5. Predictions must be observable and include three non-empty patterns: true, false, and inconclusive. The false pattern is not “the script crashed” (that is protocol failure / inconclusive).
6. Name confounders and the minimum useful experiment (smallest protocol that can discriminate true from false).
7. Confirm the planned file has no `## Results` heading.
8. If `lab/campaigns/<slug>/` exists: add hypothesis state `planned` under `state/hypotheses/`; add a relative link in `program.md`; do not paste Predictions into `program.md`.
9. Commit or otherwise freeze the planned file. **Stop if Predictions are empty.**
10. Run:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

The verifier must pass while the file is in `planned/` with no Results section.

Refuse: writing Results into `planned/`; filling Predictions after seeing spike or trial output; backfilling from a spike. Delete a dishonest planned file if one was started. Start a new planned file only with predictions written before the next run.

Hypothesis states include `planned`, `testing`, `supported`, `falsified`, `unresolved`. Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts. Do not mix those vocabularies.

Required headings in the planned file: Question, Hypothesis, Predictions, Method, Related. No Results.

## During the run

Do not edit Predictions. Store artifacts in `docs/experiments/results/yyyy-mm-dd-slug/` with a README listing files. Large binaries go under `ignored/experiment-artifacts/` with a pointer.

If the method must change in a way that invalidates Predictions, abandon this run: move nothing to successes; write a new planned file.

## After the run (write up)

1. Copy the planned body into the completed skeleton from `templates/experiment-completed.md`.
2. Fill Results, Verdict, Updated hypothesis. Verdict is about the claim, not “the script exited 0”.
3. Move the file to `successes/` when the hypothesis is supported. Move it to `failures/` when the hypothesis is falsified or the protocol failed. Delete the `planned/` copy. Set Status to match the folder.
4. If design should change, add an Agent Note in the same change ([maintain-docs](../maintain-docs/SKILL.md)).
5. Run `python scripts/verify_template.py` (scrub AppImage env as above when needed).

## Forbidden recoveries

Do not write Predictions after looking at Results. Delete the dishonest file and start a new planned experiment.

## Examples

Read [references/examples.md](references/examples.md) for three complete form-hypothesis examples (nominal, boundary refuse, different domain).
