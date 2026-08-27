# Few-shot examples — setup-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: cache API campaign through sealed evaluator

**Domain:** systems / algorithms (HTTP API, cache)

**Kind:** nominal

### Input

Operator:

> Try several cache designs and make the API faster. Budget: 8 wall-clock hours, 20 trials, stop after 5 consecutive rejected candidates. Protect `tests/api/` and `benchmarks/api-p95.json`. Mutable: cache package under `lab/` listed later. Cost approved for local hardware only.

Slug: `api-cache-p95`. `lab/templates/campaign/` exists. No planned experiment yet. Workload file `benchmarks/api-p95.json` exists.

### Decision summary

- Classification: campaign (several designs, many trials). Not a spike. Not one experiment.
- Phase 1: recommendation `proceed` after workload and budget are present.
- Phase 2: copy template to `lab/campaigns/api-cache-p95/`; disjoint mutable vs protected paths; greedy ratchet; `program.md` links experiments later; no Predictions paste; state `draft`.
- Phase 3: hard constraints = API tests pass and holdout digest unchanged; objective = p95 latency; baseline stability required; lock input lists protected paths; digests empty until sealed.
- Do not run trials. After operator seals the evaluator, hand off to `run-campaign` (baseline first).

### Actions

1. The agent emits a scope draft classified `campaign`.
2. The agent copies `lab/templates/campaign/` to `lab/campaigns/api-cache-p95/`.
3. The agent fills `campaign.yaml` and `program.md`.
4. The agent writes the evaluator specification and lock input.
5. The agent asks the operator to accept the protected set.
6. The agent runs `verify_template.py`.

### Output

Scope draft (summary): Classification `campaign`; Goal reduce API p95 under fixed contract; Blockers none; Handoff continue setup.

Campaign tree:

```text
lab/campaigns/api-cache-p95/
  program.md
  campaign.yaml
  evaluator.lock.json          # unsealed
  state/
  reports/evaluator-design-request.md
```

Evaluator specification (summary): hard constraints = `tests/api/` exit 0, holdout digest unchanged; objective = p95 latency lower-is-better; baseline stability on unchanged subject; Operator acceptance `pending`.

### Stop behavior

The agent stops for operator acceptance and seal. The agent does not start trials. After seal → `run-campaign`. Planned experiments → `run-experiment`, then link from `program.md`.

## Example 2 — Failure / boundary: NEVER STOP, git reset --hard, production traffic

**Domain:** systems / algorithms

**Kind:** failure / boundary

### Input

Operator:

> Make the API faster. NEVER STOP. If a candidate is worse, git reset --hard and try again. Use production traffic if we do not have a benchmark.

`tests/api/` exists. No checked-in workload. Production logs contain customer payloads.

### Decision summary

- Intent looks like a campaign, but preconditions fail.
- `NEVER STOP` is an unbounded loop. Refuse.
- Destructive Git reset is not a valid reject mechanism. Refuse.
- Production traffic is not an approved workload. Refuse.
- Recommendation is not `proceed`. Do not create campaign files.

### Actions

1. The agent classifies intent as campaign and records blockers.
2. The agent refuses unbounded-loop language and asks for finite limits.
3. The agent refuses `git reset --hard`.
4. The agent refuses production traffic as evaluator corpus.
5. The agent does not copy the campaign template.

### Output

```text
# Scope draft
Classification: campaign
Goal: Reduce API latency under a fixed contract (operator request).
Users: API clients.
Risks: Secret leakage from production traffic; unbounded compute; lost candidate history.
Material costs: unknown; refused until a budget exists.
Known facts: tests/api/ exists; no tracked benchmark corpus.
Assumptions: none accepted from the unbounded instructions.
Non-goals: Using production customer payloads as holdout; unbounded search; destructive Git reset.
Research questions: not opened until a workload and budget exist.
Evidence sources: invariant API tests (present); representative workload (missing).
Open questions: workload; budget; stop conditions; memory cap.
Recommendation: different-workflow until blockers clear — then campaign.
Blockers:
- no representative workload
- unbounded loop instruction refused
- destructive Git reset refused
- production traffic refused as evaluator input
Handoff: stop. Ask the operator for a finite budget, protected tests, and a checked-in or attested workload.
```

### Stop behavior

The agent stops with named blockers. The agent does not start phase 2. Fail loud.

## Example 3 — Different domain: fluid-boundary spike (early exit)

**Domain:** physics (cellular automaton sketch)

**Kind:** different domain (wrong class for campaign; early exit)

### Input

Operator:

> Sketch whether a cellular automaton could represent this fluid boundary.

No metric is named. The operator wants conceptual exploration this week.

### Decision summary

- Classification: spike. No prior hypothesis. No campaign. No evaluator.
- Path: `lab/spikes/`. Do not invent Predictions after the sketch.
- Early exit after phase 1. Do not copy `lab/templates/campaign/`.

### Actions

1. The agent classifies the work as a spike.
2. The agent creates `lab/spikes/fluid-boundary-ca/README.md` only if the operator wants it saved.
3. The agent does not write Predictions.
4. The agent does not design an evaluator.

### Output

```text
# Scope draft
Classification: spike
Goal: Sketch whether a cellular automaton can represent the named fluid boundary.
Users: the operator (exploration).
Risks: Treating a sketch as evidence of accuracy; leaking a later fake hypothesis.
Material costs: none identified (local sketch).
Known facts: operator requested conceptual exploration only.
Assumptions: “represent” means a qualitative structural analogy, not error norms.
Non-goals: Measuring numerical error; starting a campaign; writing predictions after the sketch.
Research questions: none for this spike.
Evidence sources: none yet.
Open questions: which fluid equations; which boundary; whether a metric will be required later.
Recommendation: proceed (as spike only)
Blockers: none for a sketch.
Handoff: lab/spikes/fluid-boundary-ca/. Stop. Planned experiment via run-experiment before quantitative testing.
```

Spike README (if written): Informal sketch. No hypothesis. Promotion requires `lab/experiments/planned/` with Predictions before any measurement.

### Stop behavior

The agent stops after the spike README (if written). If the operator later asks for accuracy, the agent starts `run-experiment` on a new planned file. The agent does not reuse spike notes as Predictions.
