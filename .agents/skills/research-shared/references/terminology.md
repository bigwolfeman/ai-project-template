# Research terminology

Use these terms in skills, schemas, reports, and campaign files. Do not invent synonyms.

Architecture: [Automated research campaigns](../../../notes/implemented/architecture/2026-08-24-automated-research-campaigns.md). Experiments: [lab/experiments/AGENTS.md](../../../../lab/experiments/AGENTS.md).

## Actors

| Actor | Role |
|---|---|
| The operator | The human. Owns goal, budget, protected resources, evaluator acceptance, and promotion. |
| The agent | Drafts research artifacts. Mutates only paths the manifest lists. |
| The runner | Future slice. Owns isolation, timeouts, ledger append, and candidate disposition. |
| The evaluator | Protected system that produces observations from a candidate. |
| The comparator | Classifies a candidate relative to the baseline or the current best candidate. |
| The verifier | `scripts/verify_template.py` and later campaign checks. |

The agent must not silently approve cost, safety, or irreversible work for the operator.

## Workflow kinds

**Spike** — informal exploration in `lab/spikes/`. No prior hypothesis.

**Experiment** — a protocol that tests one hypothesis. Records live under `lab/experiments/`. An experiment can require several repeated trials.

**Campaign** — a bounded research program in `lab/campaigns/<slug>/`. A campaign coordinates one or more hypotheses and many trials. It owns the operational goal, mutable scope, protected resources, budgets, comparison policy, and stopping conditions.

**Research question** — what the campaign must learn. The question does not assert an answer.

**Hypothesis** — a falsifiable claim. It has predictions, confounders, and conditions that would make a test inconclusive.

## Campaign objects

**Candidate** — one version of the mutable research subject. A code candidate uses an immutable Git commit identifier. A non-code candidate uses a content digest and a provenance record.

**Baseline** — the sealed candidate and measurement set used for comparison. The baseline includes uncertainty estimates when measurements are noisy.

**Evaluator** — the protected system that produces observations. It includes test data, scoring logic, constraints, measurement definitions, and comparison rules.

**Comparator** — classifies a candidate relative to the baseline or the current best candidate. It can use hard constraints, lexicographic objectives, Pareto dominance, confidence intervals, equivalence margins, complexity penalties, or domain-specific acceptance rules.

**Issue** — a persistent uncertainty, defect, limitation, or search obstacle. An issue records attempted interventions and observed outcomes.

**Evidence** — a result with provenance. See [evidence-standard.md](evidence-standard.md).

**Synthesis** — a belief update from a set of experiments and trials. A synthesis distinguishes supported, falsified, unresolved, and untested claims.

**Promotion** — a human-reviewed project decision that moves a research result toward production. Promotion requires tests or proofs, documentation, and an Agent Note when shipped behavior or architecture changes. The agent must not write campaign output into `src/` without operator review.

## Trial outcomes

A **trial** is one execution of one candidate under a declared protocol.

A trial outcome is one of:

| Outcome | Meaning |
|---|---|
| `accepted` | The comparator and campaign policy keep this candidate. |
| `rejected` | The comparator and campaign policy discard this candidate. The identifier remains. |
| `invalid` | The trial did not produce usable evidence. Protocol or candidate packaging failed. |
| `inconclusive` | The trial ran, but the comparator cannot classify the candidate. |
| `crashed` | Execution stopped before a complete evaluator result. |

These terms describe candidate handling. They do not state whether a scientific hypothesis is true.

The agent must not use `git reset --hard` to reject a candidate. The ledger keeps the identifier.

## Hypothesis verdicts

A hypothesis verdict is one of:

| Verdict | Meaning |
|---|---|
| `supported` | The protocol ran. The predictions held. |
| `falsified` | The protocol ran. The predictions did not hold. |
| `unresolved` | The claim is not decided. |

A synthesis may also mark a claim **untested**. Untested means no valid protocol addressed that claim.

## Experiment folders are not trial outcomes

This slice keeps `lab/experiments/planned/`, `successes/`, and `failures/`.

| Folder | Meaning |
|---|---|
| `planned/` | Hypothesis, predictions, and method. No results. |
| `successes/` | Predictions held. Hypothesis `supported`. |
| `failures/` | Hypothesis `falsified`, or the protocol failed so the hypothesis was not tested. |

The Verdict section must state which case applies. A script that exits 0 is not a supported hypothesis.

If the method cannot tell whether the hypothesis is true, that is a protocol failure. The agent files it under `failures/` with an `unresolved` claim. That folder status is not the trial outcome `inconclusive`.

## Comparator outcomes are a third vocabulary

The comparator returns `dominates`, `equivalent`, `regresses`, `mixed`, `invalid`, or `inconclusive`.

Campaign policy maps comparator outcomes to trial outcomes. The agent must not treat a comparator label as a hypothesis verdict.

## Planes

| Plane | Home |
|---|---|
| Execution | `lab/` |
| Evidence | `lab/experiments/` |
| Decision | `.agents/notes/` |
| Production | `src/` after promotion |

`program.md` links planned experiment documents. `program.md` must not copy hypotheses or predictions.
