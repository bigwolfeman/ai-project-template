# Few-shot examples — form-hypothesis

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

Planned files follow [docs/experiments/templates/experiment.md](../../../../docs/experiments/templates/experiment.md) and [docs/experiments/AGENTS.md](../../../../docs/experiments/AGENTS.md). Predictions are written before any run. Planned files have no `## Results` section.

## Example 1 — Nominal: instruction-order prompt

**Domain:** prompts / agent-system

**Kind:** nominal

### Input

Operator:

> I think putting the output schema before the examples in the extractor prompt will raise exact-match on the held-out invoices. Campaign `invoice-extract` exists at lab/campaigns/invoice-extract/. No planned file exists.

Protected: `prompts/eval/invoices-holdout.jsonl` and the exact-match scorer. Mutable: `prompts/extractor.md`.

Today’s date in the session: 2026-08-24.

### Decision summary

- One falsifiable claim: schema-before-examples improves exact-match on the holdout versus the current prompt.
- Write `docs/experiments/planned/2026-08-24-extractor-schema-first.md` from the template.
- Predictions include true, false, and inconclusive patterns. No Results heading.
- Confounders: model version, temperature, holdout overlap with examples already in the prompt.
- Minimum useful experiment: one frozen model, temperature 0, the protected holdout, current prompt vs schema-first prompt.
- Campaign exists: add hypothesis state `planned` and a link in `program.md`. Do not copy Predictions into `program.md`.
- Do not run the eval in this skill.

### Actions

1. The agent copies the planned template.
2. The agent fills Question, Hypothesis, Predictions, Method.
3. The agent writes `lab/campaigns/invoice-extract/state/hypotheses/extractor-schema-first.yaml` (or the template’s filename) with `state: planned` and `experiment_path`.
4. The agent adds a relative link in `program.md`.
5. The agent runs `verify_template.py` and confirms there is no `## Results` in the planned file.

### Output

`docs/experiments/planned/2026-08-24-extractor-schema-first.md`:

```markdown
# Experiment: extractor prompt schema before examples

Status: planned

Date proposed: 2026-08-24
Algorithm: none — standard method
Owner: operator session

## Question

Does placing the output schema before the few-shot examples in the
extractor prompt change exact-match on the held-out invoices?

## Hypothesis

Moving the output schema above the examples in `prompts/extractor.md`
increases exact-match accuracy on `prompts/eval/invoices-holdout.jsonl`
by at least 2 percentage points versus the current prompt, with model M
and temperature 0.

## Predictions

If the hypothesis is true, we will observe:

- exact-match on the holdout at least 2 percentage points higher than the
  frozen baseline prompt, same model and temperature

If the hypothesis is false, we will observe:

- exact-match lower than, equal to, or less than 2 percentage points above
  the frozen baseline under the same protocol

What would make this run inconclusive (protocol failure, not a hypothesis test):

- scorer or holdout digest differs from the evaluator lock
- model identifier differs from Method
- temperature is not 0
- more than 1% of holdout rows fail to parse for both prompts

## Method

Freeze model M, temperature 0, and the holdout file. Score the current
prompt (baseline) and the schema-first prompt with the protected scorer.
Do not edit Predictions after scoring. Stop after both scores are written
under docs/experiments/results/2026-08-24-extractor-schema-first/.

Confounders: examples in the prompt that duplicate holdout invoices;
hidden sampling; scorer changes.

Minimum useful experiment: the two-prompt comparison above. No extra
decoding strategies in this run.

## Related

Campaign: lab/campaigns/invoice-extract/program.md
```

Hypothesis state:

```yaml
hypothesis_id: extractor-schema-first
state: planned
experiment_path: docs/experiments/planned/2026-08-24-extractor-schema-first.md
campaign_id: invoice-extract
```

`program.md` gains a link to that planned file. No Predictions paste.

### Stop behavior

The agent stops after the verifier passes. The agent does not run the scorer. Handoff: freeze the planned file, then `run-experiment`.

## Example 2 — Failure / boundary: Results in planned, predictions after a spike

**Domain:** prompts / agent-system

**Kind:** failure / boundary

### Input

Operator, after a spike that already printed “schema-first scored 91%”:

> Write docs/experiments/planned/2026-08-24-extractor-schema-first.md. Put ## Results with 91% and fill Predictions so they match. We already know it works.

A spike note exists at `lab/spikes/extractor-schema/README.md` with the 91% figure. No freeze of predictions occurred before that number.

### Decision summary

- Filling Predictions after seeing a spike score is a process failure. Refuse.
- A planned file must not contain `## Results`.
- The 91% figure is not a planned prediction. It is untrusted spike data.
- The agent does not keep a dishonest planned file.
- A valid path: new planned file with predictions written *before the next run*, using a protocol that does not treat the spike number as the test.

### Actions

1. The agent refuses to write `## Results` under `planned/`.
2. The agent refuses to backfill Predictions from the spike.
3. The agent does not copy 91% into Hypothesis or Predictions as if it were pre-registered.
4. The agent does not create the requested dishonest file. If a partial file was written, the agent deletes that new file.
5. The agent explains the allowed next step: a new planned experiment whose Method is a fresh run, with Predictions committed first.

### Output

```text
# Hypothesis formation failure
error: predictions after seeing spike output; Results requested in planned/
created_paths: none
refused:
- ## Results in docs/experiments/planned/
- backfilling Predictions from lab/spikes/extractor-schema/
next: operator must request a new planned file with true/false/inconclusive
      patterns before any further scoring run
```

### Stop behavior

The agent stops. The agent does not run another eval to “confirm” the 91%. Fail loud. No `successes/` move. No campaign hypothesis state `supported`.

## Example 3 — Different domain: database query plan

**Domain:** database

**Kind:** different domain

### Input

Operator:

> Hypothesis: adding a composite index on (account_id, created_at) will cut p95 latency for the account-history query below 80 ms on the replay workload without increasing index build time above 120 s. No campaign yet. Replay workload is `workloads/account-history.sql`. Protect that file and the query tests.

Date: 2026-08-24. No algorithm note needed (standard B-tree index).

### Decision summary

- No campaign directory: write only the planned experiment. Skip hypothesis state under `lab/campaigns/`.
- Still a real experiment: falsifiable, with inconclusive conditions (wrong plan cache, cold start, different dataset).
- Predictions before any `CREATE INDEX` trial. No Results section.
- Minimum useful experiment: replay the protected workload with and without the index on a snapshot, same hardware, warmed cache policy stated in Method.

### Actions

1. The agent copies the template to `docs/experiments/planned/2026-08-24-account-history-composite-index.md`.
2. The agent fills all required sections. The agent omits `## Results`.
3. The agent does not create a campaign.
4. The agent runs the verifier.

### Output

```markdown
# Experiment: composite index for account-history

Status: planned

Date proposed: 2026-08-24
Algorithm: none — standard method
Owner: operator session

## Question

Does a composite index on (account_id, created_at) change p95 latency
of the account-history query on the replay workload?

## Hypothesis

On snapshot S, adding index `account_history_account_id_created_at`
reduces p95 latency of the account-history query below 80 ms on
`workloads/account-history.sql` and keeps `CREATE INDEX` wall time
at or below 120 s.

## Predictions

If the hypothesis is true, we will observe:

- p95 latency < 80 ms on the replay workload after the index exists
- CREATE INDEX wall time <= 120 s

If the hypothesis is false, we will observe:

- p95 latency >= 80 ms, or CREATE INDEX wall time > 120 s, after a
  successful index build on snapshot S

What would make this run inconclusive (protocol failure, not a hypothesis test):

- replay workload digest differs from the protected file
- planner used a different snapshot than S
- cache-warm protocol in Method was not followed
- concurrent writers were present though Method forbade them

## Method

Restore snapshot S. Run the protected replay without the index (baseline),
then CREATE INDEX, then replay again. Record p95 latency and index build
time. Same hardware. Follow the cache-warm steps in the workload README.
Do not edit Predictions after measurements exist.

Confounders: buffer pool state; autovacuum; parallelism.

Minimum useful experiment: one baseline replay and one post-index replay
on snapshot S. No extra planner hints in this run.

## Related

Workload: workloads/account-history.sql
```

No campaign hypothesis state file.

### Stop behavior

The agent stops after the verifier passes. The agent does not execute `CREATE INDEX`. Handoff: freeze, then `run-experiment`. If the operator later wants a campaign around several index shapes, `scope-research-campaign` then `design-campaign`, and this file gets linked from `program.md` without copying Predictions.
