# AGENTS.md — Experiments

Experiments are measured inquiry. They are not spikes (`lab/`), not design decisions (Agent Notes), and not incident reports (postmortems).

The scientific method is the format. **Predictions are written and committed before any run.** Filling predictions after seeing results is a process failure; delete the file and start over if that happened.

## Layout

```
docs/experiments/
  algorithms/     Writeups (and notebooks) on methods — not run records
  planned/        Hypothesis + predictions + method; no results
  successes/      Runs whose predictions held (hypothesis supported)
  failures/       Runs that falsified the hypothesis or broke the protocol
  results/        Data, figures, notebooks outputs; linked from the writeup
  templates/      Copy these; do not edit in place as a live record
```

Naming for run records: `yyyy-mm-dd-short-slug.md` in `planned/`, `successes/`, or `failures/`.

Algorithm writeups: `algorithms/yyyy-mm-dd-short-slug.md` plus optional `algorithms/yyyy-mm-dd-short-slug.ipynb`.

Result artifacts: `results/yyyy-mm-dd-short-slug/` matching the run file's slug. Large binaries go in `ignored/experiment-artifacts/` with a pointer file in `results/`.

## Lifecycle

1. If the method is new or non-obvious, write or update an algorithm note first.
2. Copy `templates/experiment.md` to `planned/yyyy-mm-dd-slug.md`. Fill Question, Hypothesis, Predictions, Method. Commit.
3. Run the experiment. Do not edit Predictions. If the method must change, write why under Method as an amendment dated after the original commit; if the predictions no longer apply, reject this run and open a new planned file.
4. Store artifacts under `results/yyyy-mm-dd-slug/`.
5. Fill Results, Verdict, and Updated hypothesis. Move the file to `successes/` or `failures/`. Set `Status:` to match.
6. If the outcome changes shipped design, add or update an Agent Note in the same change.

## Status values

Must match the folder:

- `Status: planned`
- `Status: success`
- `Status: failure`

`planned/` files must contain `## Predictions` and `## Method` with real content. They must not contain a `## Results` section (use the placeholder sentence in the template's comment only — the live file omits Results entirely).

`successes/` and `failures/` must contain Predictions, Method, Results, Verdict, and Updated hypothesis.

## Verdict

- **success**: the hypothesis was tested and the predictions held.
- **failure**: the hypothesis was tested and the predictions did not hold, *or* the protocol failed so the hypothesis was not actually tested. Say which in Verdict.
- Do not file a "success" because the code ran. Success is about the claim.

## Inconclusive

If you cannot tell whether the hypothesis is true, that is a **failure of the protocol**. File under `failures/`, state what the method could not distinguish, and write the next planned experiment.

## Forbidden

- Results in `planned/`
- Editing Predictions after artifacts exist
- An experiment writeup with no link to method or data
- Dumping unlabeled numbers in `results/` with no matching writeup
- Turning a `lab/` spike into an experiment by writing predictions after the fact
