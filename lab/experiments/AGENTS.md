# AGENTS.md — Experiments

Experiments are measured inquiry. They are not spikes (`lab/spikes/`), not campaigns (`lab/campaigns/`), not design decisions (Agent Notes), and not incident reports (postmortems).

The scientific method is the format. **Predictions are written and committed before any run.** Filling predictions after seeing results is a process failure; delete the file and start over if that happened.

A **campaign** may coordinate several experiment files. The campaign `program.md` must link those files. It must not copy their hypotheses or predictions. Lab rules: [lab/AGENTS.md](../AGENTS.md).

## Layout

```
lab/experiments/
  algorithms/     Writeups (and notebooks) on methods — not run records
  planned/        Hypothesis + predictions + method; no results
  successes/      Predictions held at or past the stated strong bar (supported)
  mixed/          Partial signal: some predictions held, or the effect is real but below the strong bar
  refuted/       Solid dead ends: protocol sound, effect absent or reversed, no rescue left to try
  results/        Data, figures, notebooks outputs; linked from the writeup
  templates/      Copy these; do not edit in place as a live record
```

Keep `planned/`, `successes/`, `mixed/`, and `refuted/` in this slice.

Naming for run records: `yyyy-mm-dd-short-slug.md` in `planned/`, `successes/`, `mixed/`, or `refuted/`.

Algorithm writeups: `algorithms/yyyy-mm-dd-short-slug.md` plus optional `algorithms/yyyy-mm-dd-short-slug.ipynb`.

Result artifacts: `results/yyyy-mm-dd-short-slug/` matching the run file's slug. Large binaries go in `ignored/experiment-artifacts/` with a pointer file in `results/`.

## Write the idea down as pseudocode

Every Method section holds pseudocode of the change under test, in a fenced block. The verifier checks for the fence. A reader should follow the idea without opening the diff. If the method is new, the algorithm writeup holds the full pseudocode and Method links to it.

## Lifecycle

1. If the method is new or non-obvious, write or update an algorithm note first.
2. Copy `templates/experiment.md` to `planned/yyyy-mm-dd-slug.md`. Fill Question, Hypothesis, Predictions, Method. Predictions name a scalar, a strong bar, and a dead-end bar before the run. Commit.
3. Run the experiment. Do not edit Predictions. If the method must change, write why under Method as an amendment dated after the original commit; if the predictions no longer apply, reject this run and open a new planned file.
4. Store artifacts under `results/yyyy-mm-dd-slug/`.
5. Fill Results, Verdict, and Updated hypothesis. Move the file to `successes/`, `mixed/`, or `refuted/`. Set `Status:` to match.
6. If the outcome changes shipped design, add or update an Agent Note in the same change.

## Status values

Must match the folder:

- `Status: planned`
- `Status: success`
- `Status: mixed`
- `Status: refuted`

`planned/` files must contain `## Predictions` and `## Method` with real content. They must not contain a `## Results` section (use the placeholder sentence in the template's comment only — the live file omits Results entirely).

`successes/`, `mixed/`, and `refuted/` must contain Predictions, Method, Results, Verdict, and Updated hypothesis.

## Verdict

Folder status is not the same as a hypothesis verdict.

Hypothesis verdicts:

- **supported**: the predictions held and the measured scalar cleared the strong bar. File under `successes/`.
- **mixed**: the protocol was sound and the result carries signal, but it is not a clean win. File under `mixed/`.
- **refuted**: the protocol was sound and the predictions did not hold. File under `refuted/`, and only when the result is a solid dead end (see below).
- **unresolved**: the method could not tell whether the hypothesis is true. File under `refuted/` as a protocol failure. This verdict does not kill the idea. Write the next planned experiment.

Do not file a "success" because the code ran. Success is about the claim.

## Mixed results

Models over-read results. A small gain becomes "confirmed". A missed bar becomes "refuted". Both errors kill good ideas, so the agent files by comparing the measurement to the bars written before the run.

File under `mixed/` when any of these holds:

- The scalar moved in the predicted direction, beyond noise, but did not reach the strong bar.
- Some predictions held and others did not. For example, quality rose and cost rose too.
- The effect appears in one condition (seed set, scale, dataset slice) and not in another.
- The result beats the null but a named confounder could explain part of it.

A mixed Verdict names what held, what did not, and the one experiment that would split the two. It does not claim the idea works. It does not claim the idea is dead.

## Failures are solid dead ends

File under `refuted/` with verdict `refuted` only when all of these hold:

- The protocol ran to completion and the evaluator was valid.
- The measured scalar is at the null, or moves against the prediction, beyond noise.
- The Verdict lists the variants the agent tried or considered, and why none can rescue the idea.
- The Updated hypothesis states what the failure rules out, so no later session repeats it.

If one of these is missing, the result is `mixed` or `unresolved`, not `refuted`. A missed strong bar alone is not a dead end. A crash is never a dead end.

When the agent cannot decide between `mixed` and `refuted`, it files `mixed` and says why.

## Trials vs experiments

A **trial** is one execution of one candidate. Trial outcomes are `accepted`, `rejected`, `invalid`, `inconclusive`, and `crashed`. Those words describe candidate handling. They are not hypothesis verdicts.

The campaign ledger is execution evidence. Experiment documents summarize at the hypothesis level. Do not paste trial JSONL into the experiment writeup.

Link the evaluator identity, the protocol, and the artifact pointers needed to interpret the result. Generated campaign reports live under `lab/campaigns/<slug>/reports/`. Those reports are not experiment verdicts.

## Inconclusive

If you cannot tell whether the hypothesis is true, that is a **failure of the protocol**. File under `refuted/`, state what the method could not distinguish, and write the next planned experiment. The idea stays open.

A trial outcome of `inconclusive` is not this verdict. The campaign may continue. The experiment file stays in `planned/` until the hypothesis has a verdict.

## Forbidden

- Results in `planned/`
- Editing Predictions after artifacts exist
- An experiment writeup with no link to method or data
- Dumping unlabeled numbers in `results/` with no matching writeup
- Turning a `lab/spikes/` spike into an experiment by writing predictions after the fact
- Copying experiment predictions into campaign `program.md`
- Using trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) as hypothesis verdicts
