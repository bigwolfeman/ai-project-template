---
name: run-experiment
description: Use when proposing, running, or writing up an experiment. Enforces predictions-before-results and the docs/experiments layout.
---

# Run an experiment

Read [docs/experiments/AGENTS.md](../../../docs/experiments/AGENTS.md) first. Do not start from `lab/` after the fact.

## Before any run

1. If the method is non-obvious, add or update `docs/experiments/algorithms/yyyy-mm-dd-slug.md`.
2. Copy `docs/experiments/templates/experiment.md` to `docs/experiments/planned/yyyy-mm-dd-slug.md`.
3. Fill Question, Hypothesis, Predictions, Method. Predictions must be observable and include a falsifying pattern and an inconclusive pattern.
4. Commit or otherwise freeze that file. **Stop if Predictions are empty.**
5. Run `python scripts/verify_template.py`. It must pass while the file is still in `planned/` with no Results section.

## During the run

Do not edit Predictions. Store artifacts in `docs/experiments/results/yyyy-mm-dd-slug/` with a README listing files. Large binaries go under `ignored/experiment-artifacts/` with a pointer.

If the method must change in a way that invalidates Predictions, abandon this run: move nothing to successes; write a new planned file.

## After the run

1. Copy the planned body into the completed skeleton from `templates/experiment-completed.md`.
2. Fill Results, Verdict, Updated hypothesis. Verdict is about the claim, not "the script exited 0".
3. Move the file to `successes/` or `failures/`. Delete the `planned/` copy. Set Status to match the folder.
4. If design should change, add an Agent Note in the same change.
5. Run `python scripts/verify_template.py`.

## Forbidden recoveries

Do not write Predictions after looking at Results. Delete the dishonest file and start a new planned experiment.
