# Few-shot examples — design-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: tokenizer and architecture campaign

**Domain:** machine learning

**Kind:** nominal

### Input

Scope draft (already classified `campaign`, recommendation `proceed` after the operator approved a GPU-hour budget):

> Optimize a tokenizer and model architecture together on a language-modeling corpus. Budget: 48 GPU-hours, 30 trials, stop after 8 consecutive rejected candidates. Protect the validation byte corpus and the bits-per-byte metric code.

Operator slug: `tok-arch-lm`. No planned experiment file exists yet.

`lab/templates/campaign/` exists.

### Decision summary

- Copy the template to `lab/campaigns/tok-arch-lm/`. Do not edit the template in place.
- Fill `campaign.yaml` with disjoint mutable and protected paths.
- Isolation: Git worktrees under `ignored/research/tok-arch-lm/worktrees/`.
- Exploration: greedy ratchet unless the operator stated a compound tokenizer-plus-architecture change that needs a bounded branch.
- `program.md` links experiments. It does not copy predictions. None exist yet, so the program says so and points at `form-hypothesis`.
- State stays `draft`. Do not seal the evaluator lock. Do not append ledger events.
- Evaluator design request must reject per-token loss as the sole cross-candidate metric.

### Actions

1. The agent verifies `lab/templates/campaign/` exists.
2. The agent verifies `lab/campaigns/tok-arch-lm/` does not exist.
3. The agent copies the template directory.
4. The agent fills `campaign.yaml` using the template field names. Budget includes 48 GPU-hours (total) and 8 consecutive rejected candidates (stagnation).
5. The agent sets protected paths: validation bytes, metric code, tests. Mutable paths: tokenizer and model source listed in the manifest.
6. The agent writes `program.md` with goal, non-goals, budget summary, and a link placeholder to planned experiments.
7. The agent writes `reports/evaluator-design-request.md` asking for bits per byte, throughput, memory, and model size.
8. The agent asks the operator to review budget and protected paths.
9. The agent runs `verify_template.py`.

### Output

Created:

```text
lab/campaigns/tok-arch-lm/
  program.md
  campaign.yaml
  evaluator.lock.json          # unsealed template copy
  state/                       # draft
  reports/evaluator-design-request.md
```

`program.md` excerpt (predictions not copied):

```markdown
# Campaign: tokenizer and architecture

Goal: Find a tokenizer-plus-architecture pair that improves bits per byte
on the protected validation bytes within the GPU-hour budget.

Non-goals: Promoting checkpoints into src/; changing the holdout bytes.

Experiments: none yet. Form hypotheses with form-hypothesis, then link
the planned files here. Do not paste Predictions into this file.

Budget: 48 GPU-hours; 30 trials; stop after 8 consecutive rejected candidates.
```

Evaluator design request (summary): vocabulary-independent metric (bits per byte); protect validation bytes and metric calculation; add throughput, memory, and model-size measurements; repeated seeds if training noise is material.

Campaign state: `draft`.

### Stop behavior

The agent stops in `draft`. The agent does not run training. The agent hands off to `design-evaluator`, then `form-hypothesis`. The agent does not start a research loop. This slice has no runner.

## Example 2 — Failure / boundary: missing template, predictions pasted into program.md

**Domain:** machine learning (same family of request)

**Kind:** failure / boundary

### Input

Operator:

> Create lab/campaigns/tok-arch-lm/. Put the hypothesis in program.md:

```markdown
## Predictions
If true, validation bits per byte drops by 3%.
```

`lab/templates/campaign/` is **absent** (schemas and templates not shipped yet, or the path was never created).

### Decision summary

- The skill’s first mechanical step is to copy `lab/templates/campaign/`. That path is missing. Fail loud. Do not invent a campaign tree from memory.
- Even if the template existed, pasting `## Predictions` into `program.md` is forbidden. Experiments own predictions. The program links them.
- The agent does not create a partial `lab/campaigns/tok-arch-lm/` that later looks like a valid campaign.

### Actions

1. The agent checks `lab/templates/campaign/`.
2. The agent reports `missing path: lab/templates/campaign/` and stops the copy.
3. The agent refuses to write `## Predictions` into any `program.md`.
4. The agent does not create `lab/campaigns/tok-arch-lm/`.
5. The agent tells the operator that `lab/templates/campaign/` must exist before this skill can continue, and that predictions belong in `docs/experiments/planned/`.

### Output

```text
# Campaign design failure
slug: tok-arch-lm
error: missing lab/templates/campaign/
refused: copying predictions into program.md
created_paths: none
state_transition: none
handoff: stop until the campaign template exists; then design-campaign;
         form-hypothesis writes docs/experiments/planned/; program.md links only.
```

### Stop behavior

The agent stops with a missing-path error. The agent does not synthesize `campaign.yaml` by hand as a substitute for the template. The agent does not use a destructive Git reset. Fail loud.

## Example 3 — Different domain: intermittent deadlock

**Domain:** bug investigation

**Kind:** different domain

### Input

Operator, after a scope draft classified `bug-investigation` as a campaign:

> Find and fix an intermittent deadlock in the worker pool. Budget: 12 wall-clock hours, 40 trials, stop after 6 consecutive inconclusive reproductions. Protect the failing trace and the stress harness. Do not merge to src/ from the campaign.

Slug: `worker-deadlock`. `lab/templates/campaign/` exists. No planned experiment yet.

### Decision summary

- This is a campaign: competing causal explanations and many trials.
- Reproduction and stress protocols belong in the evaluator, not as a single unfalsifiable “fix it” hope.
- “Did not reproduce once” is inconclusive, not success. The program must say that. The program must not call that a hypothesis verdict.
- Isolation: worktrees. Mutable: worker-pool source listed in the manifest. Protected: failing trace, stress harness, regression tests.
- Exploration: bounded issue-centric search is appropriate. Greedy “first passing test wins” is not enough for an intermittent fault.
- `program.md` will later link experiments for each competing cause. It will not copy their predictions.
- Promotion only after stress and regression tests pass, and only with human review.

### Actions

1. The agent copies `lab/templates/campaign/` to `lab/campaigns/worker-deadlock/`.
2. The agent fills `campaign.yaml` with the budget (12 hours total; 6 consecutive inconclusive as stagnation) and stop conditions.
3. The agent sets exploration to bounded branch or issue-centric search within the template’s exploration fields. Maximum branch depth is finite.
4. The agent writes `program.md` with reproduction confidence rule: a single non-repro is `inconclusive`, not a fix.
5. The agent writes an evaluator design request: preserve the failing trace; stress protocol; regression tests; do not treat one clean run as acceptance.
6. The agent leaves state `draft` and does not hand-write ledger rows for imagined trials.

### Output

`lab/campaigns/worker-deadlock/` as a `draft` campaign.

`program.md` excerpt:

```markdown
# Campaign: worker-pool deadlock

Goal: Identify a cause of the intermittent deadlock and produce a candidate
that passes stress and regression tests.

Non-goals: Silent merge to src/; calling a single non-reproduction a fix.

Experiments: none yet. Link planned files here after form-hypothesis.
Do not paste Predictions.

Reproduction confidence: one passing run after a flake is inconclusive.
Promotion requires the operator and passing stress plus regression tests.
```

Evaluator design request: protect failing trace and harness; track competing causes as issues (issue records come in a later skill); trial outcomes stay `accepted|rejected|invalid|inconclusive|crashed`.

### Stop behavior

The agent stops in `draft`. The agent hands off to `design-evaluator` and `form-hypothesis`. The agent does not start an unbounded “keep trying until it deadlocks” loop. The agent does not reset Git to hide failed candidates.
