# Phase 1 — Classify and scope

The agent converts a broad goal into a classification and a scope draft. The agent does not start a campaign, write predictions, or mutate production code in this phase.

## Classification tests

- Informal exploration with no prior hypothesis → **spike**. Path: `lab/spikes/`.
- One falsifiable claim with predictions before any run → **experiment**. Path: `docs/experiments/` via [run-experiment](../../run-experiment/SKILL.md).
- Bounded program that coordinates one or more experiments and many trials → **campaign**. Path: `lab/campaigns/<slug>/` in phase 2.
- Defect with a reproduction protocol that may need competing explanations → **bug-investigation**. Usually a campaign. A single already-falsifiable fix claim may be one experiment.
- Choice of architecture, process, or shipped behavior without a measurement protocol → **design-decision**. Path: `.agents/notes/`.

The agent records one primary class.

The agent does not invent a hypothesis after seeing a spike outcome.

The agent does not treat a trial outcome as a hypothesis verdict.

## Scope steps (detail)

1. Restate the goal in one sentence.
2. List users, risks, and material costs separately.
3. Separate known facts from assumptions. Do not mix them.
4. Name evidence sources (tests, traces, datasets, instruments, proofs).
5. Classify with the tests above.
6. Write non-goals.
7. Write bounded research questions. Each question does not assert an answer.
8. Ask for cost approval when API, cloud, hardware, or external-service cost is material.
9. Emit the scope draft. Fill every heading. Write `unknown` when a value is unknown and add an open question.

## Blockers that stop the phase

- Missing operator goal
- Ambiguous classification (ask the operator; do not pick silently)
- Unapproved material cost
- Performance campaign with no representative workload
- Operator instruction to `NEVER STOP` or run an unbounded loop
- Operator instruction to use `git reset --hard` to discard candidates
- Production traffic proposed as holdout without attestation (secrets and instability)

## Authorized write in this phase

Spike only: `lab/spikes/<slug>/README.md` when the operator wants the sketch saved.

The README must state that the spike has no hypothesis. Promotion to measurement requires a new planned experiment with Predictions written before any run.

## Refusals

The agent refuses unbounded-loop language. The agent asks for a finite trial count and wall-clock limit.

The agent refuses destructive Git reset. Rejected candidates keep immutable identifiers.

The agent does not create `lab/campaigns/<slug>/` or `docs/experiments/planned/` in this phase.
