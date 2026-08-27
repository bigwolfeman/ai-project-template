# Few-shot examples — run-experiment (form hypothesis)

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

Planned files follow [lab/experiments/templates/experiment.md](../../../../lab/experiments/templates/experiment.md) and [lab/experiments/AGENTS.md](../../../../lab/experiments/AGENTS.md). Predictions are written before any run. Planned files have no `## Results` section.

## Example 1 — Nominal: instruction-order prompt

**Domain:** prompts / agent-system

**Kind:** nominal

### Input

Operator:

> I think putting the output schema before the examples in the extractor prompt will raise exact-match on the held-out invoices. Campaign `invoice-extract` exists at lab/campaigns/invoice-extract/. No planned file exists.

Protected: `prompts/eval/invoices-holdout.jsonl` and the exact-match scorer. Mutable: `prompts/extractor.md`. Date: 2026-08-24.

### Decision summary

- One falsifiable claim. Write `lab/experiments/planned/2026-08-24-extractor-schema-first.md`.
- Predictions include true, false, and inconclusive. No Results heading.
- Campaign exists: hypothesis state `planned` and a link in `program.md`. Do not copy Predictions.
- Do not run the eval until freeze.

### Actions

1. The agent copies the planned template and fills required sections.
2. The agent writes hypothesis state under the campaign and links `program.md`.
3. The agent runs `verify_template.py` and confirms no `## Results`.

### Output

Planned file with Question, Hypothesis, Predictions (true / false / inconclusive), Method, Related. Campaign hypothesis state `planned`. `program.md` gains a link only.

### Stop behavior

The agent stops after freeze. Then run the protocol. Then write up under successes/ or failures/.

## Example 2 — Failure / boundary: Results in planned, predictions after a spike

**Domain:** prompts / agent-system

**Kind:** failure / boundary

### Input

Operator, after a spike that already printed “schema-first scored 91%”:

> Write lab/experiments/planned/2026-08-24-extractor-schema-first.md. Put ## Results with 91% and fill Predictions so they match.

Spike note at `lab/spikes/extractor-schema/README.md` has the 91% figure. No freeze before that number.

### Decision summary

- Filling Predictions after seeing a spike score is a process failure. Refuse.
- A planned file must not contain `## Results`.
- Do not keep a dishonest planned file.

### Actions

1. The agent refuses Results under `planned/`.
2. The agent refuses backfilling Predictions from the spike.
3. The agent does not create the requested dishonest file.

### Output

```text
# Hypothesis formation failure
error: predictions after seeing spike output; Results requested in planned/
created_paths: none
next: new planned file with true/false/inconclusive patterns before any further scoring run
```

### Stop behavior

The agent stops. Fail loud. No successes/ move. No hypothesis state `supported`.

## Example 3 — Different domain: database query plan

**Domain:** database

**Kind:** different domain

### Input

Operator:

> Hypothesis: adding a composite index on (account_id, created_at) will cut p95 latency for the account-history query below 80 ms on the replay workload without increasing index build time above 120 s. No campaign yet. Protect `workloads/account-history.sql` and the query tests.

Date: 2026-08-24.

### Decision summary

- No campaign: write only the planned experiment.
- Predictions before any `CREATE INDEX` trial. No Results section.
- Minimum useful experiment: replay with and without the index on a snapshot.

### Actions

1. The agent writes `lab/experiments/planned/2026-08-24-account-history-composite-index.md`.
2. The agent fills all required sections. The agent omits `## Results`.
3. The agent runs the verifier. The agent does not execute `CREATE INDEX` until freeze.

### Output

Planned file with falsifiable Hypothesis, three prediction patterns, Method naming snapshot S and the protected workload. No campaign hypothesis state.

### Stop behavior

The agent stops after freeze. Handoff: run, then write up. If the operator later wants several index shapes as a program, use [setup-campaign](../../setup-campaign/SKILL.md), then link this file from `program.md` without copying Predictions.
