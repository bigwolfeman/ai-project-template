# Few-shot examples — audit-research-integrity

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

The agent does not run `git reset --hard`. That command is a finding when used to reject a candidate.

## Example 1 — Nominal: frozen predictions and matching digests

**Domain:** physics simulation

**Kind:** nominal

### Input

Campaign `nbody-step` is `stopped`. Operator asks for an audit before synthesis.

Facts the agent can read:

- `docs/experiments/planned/2026-08-01-energy-drift.md` was committed on 2026-08-01 with Predictions and no Results. First trial timestamp in the ledger is 2026-08-02T12:00:00Z.
- `evaluator.lock.json` lists `eval/invariants.py` and `fixtures/holdout.h5`. Recomputed SHA-256 matches.
- Ledger events have required provenance fields.
- `campaign.yaml` still has the operator-approved wall-clock and stagnation limits.
- `program.md` has stop conditions. No `NEVER STOP`. No `git reset --hard`.
- Metric is energy drift on protected fixtures, not a gameable substitute.
- No synthesis report yet, so cherry-picking is checked against the ledger only (no omitted-negative report yet).

### Decision summary

- Prediction freeze precedes trials. Pass that check.
- Digests match. Do not abort.
- Remaining checks are clean or at most non-blocking (for example a ledger size warning under 10 MiB).
- Verdict `pass` or `pass_with_risks`. Synthesis may proceed after this report.

### Actions

1. The agent recomputes lock digests. They match.
2. The agent compares planned-file freeze time to the first trial timestamp.
3. The agent scans for unbounded-loop language and `git reset --hard`.
4. The agent writes `reports/integrity-audit.md` with every check named.
5. The agent does not change `evaluator.lock.json`.

### Output

```text
# Integrity audit
Campaign: nbody-step
...
## Checks
Prediction timestamps: pass (planned freeze 2026-08-01 before first trial 2026-08-02)
Protected-resource digests: pass
Provenance: pass
Repeated interventions: pass
Cherry-picked evidence: pass (no synthesis yet; ledger not filtered)
Metric gaming: pass
Undeclared budget changes: pass
Unsupported certainty: pass
Unbounded loops: pass
git reset --hard as candidate rejection: pass (not used)

## Findings
Blocking: none
Non-blocking risks: none

## Remediation
Required remediation: none
Operator review required: no

## Verdict
pass
```

### Stop behavior

The agent stops with verdict `pass`. The agent hands off to `synthesize-campaign`. The agent does not start trials. The agent does not promote to `src/`.

## Example 2 — Failure / boundary: evaluator digest changed during a trial

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Input evidence:

- Candidate score improves.
- The evaluator digest changed during the trial.

Campaign `tok-arch-lm` was `running`. Lock listed `eval/bpb.py`. Bytes on disk no longer match the lock. Ledger shows a trial with improved bits per byte.

Operator:

> The score got better. Keep going.

### Decision summary

- Digest mismatch is abort-class. File permissions do not excuse it.
- Mark the trial invalid. Abort the campaign. Preserve logs and candidate identifiers.
- Create an integrity issue. Require operator review before any resume.
- Resume is a new campaign or a reviewed revision. Do not set `aborted` back to `running`.
- Do not synthesize. Do not promote. Do not “fix” the lock to the new bytes.

### Actions

1. The agent recomputes the digest of `eval/bpb.py`. It differs from the lock.
2. The agent writes blocking finding `evaluator-digest-mismatch`.
3. The agent sets campaign projection `state` to `aborted` and `stop_reason` to that finding.
4. The agent writes `state/issues/evaluator-digest-mismatch.md`.
5. The agent writes `reports/integrity-audit.md` with verdict `fail_abort`.
6. The agent refuses the operator request to continue.

### Output

```text
# Integrity audit
Campaign: tok-arch-lm
Campaign state before audit: running
Campaign state after audit: aborted

## Checks
Protected-resource digests: FAIL eval/bpb.py lock digest != file bytes
...

## Findings
Blocking:
- evaluator-digest-mismatch during trial <id>; candidate score improvement is not evidence
Non-blocking risks: none recorded beyond the abort

## Remediation
Required remediation: preserve logs and candidate ids; do not resume this campaign;
  operator starts a new campaign or a reviewed revision; do not rewrite the lock
Operator review required: yes

## Verdict
fail_abort
```

### Stop behavior

The agent stops immediately after confirming the mismatch. The agent does not continue the research loop. The agent does not treat the improved score as a valid trial. Fail loud.

## Example 3 — Different domain: cherry-picking, metric gaming, unbounded loop, reset --hard, backfilled predictions

**Domain:** database query tuning (also covers process failures that appear in any domain)

**Kind:** different domain

### Input

Campaign `query-planner` is `stopped`. Operator asks for an audit before promotion.

Observed:

- `docs/experiments/planned/2026-08-20-index-only.md` contains `## Results` and Predictions that match the already-finished run. Git history shows the planned file first appeared after the trial timestamps.
- A draft `reports/synthesis.md` cites two accepted trials and omits five rejected trials that used the same hypothesis.
- Sole cross-candidate metric is “rows examined” while the planner can change cardinality estimates; protected holdout traces sit under a mutable path `subject/bench/`.
- `program.md` says `NEVER STOP` and has no stagnation limit in the copied summary. `campaign.yaml` `max_trial_count` was raised from 20 to 500 with no operator record.
- Ledger `reason` text on rejected candidates: `git reset --hard to discard bad plan`.
- A proof note in `reports/` says the cost model is “proved correct” from a simplified integer model.

### Decision summary

- Backfilled predictions are blocking. The dishonest planned file is not repaired in place.
- Cherry-picking in the draft synthesis is blocking for any later synthesis that keeps that omission.
- Metric gaming and holdout-on-mutable-path are blocking.
- Unbounded loop language and undeclared budget change are blocking.
- `git reset --hard` to reject candidates is blocking. The agent does not run that command.
- “Proved correct” for a simplified model is a finding (unsupported certainty).
- Verdict `fail_abort`. Promotion does not proceed.

### Actions

1. The agent records each check with a path and identifier.
2. The agent does not delete the planned file until the operator confirms; the report states that evidence-standard requires deletion and a new planned experiment.
3. The agent does not rewrite the ledger to hide `git reset --hard`.
4. The agent writes `reports/integrity-audit.md` with verdict `fail_abort`.
5. The agent may set campaign state `aborted` if it is not already.

### Output

```text
# Integrity audit
Campaign: query-planner
...
## Checks
Prediction timestamps: FAIL planned file after trial timestamps; Results in planned/
Protected-resource digests: FAIL or warn if holdout path is mutable and unlocked
Provenance: fail if evaluator results omit required fields
Repeated interventions: record if the same index change was retried without new evidence
Cherry-picked evidence: FAIL draft synthesis omits five rejected trials
Metric gaming: FAIL rows-examined sole metric; holdout under subject/bench/
Undeclared budget changes: FAIL max_trial_count 20 → 500
Unsupported certainty: FAIL "proved correct" on simplified cost model
Unbounded loops: FAIL NEVER STOP in program.md
git reset --hard as candidate rejection: FAIL ledger reasons

## Findings
Blocking: backfill; cherry-pick; metric gaming; budget change; unbounded loop;
  git reset --hard; forbidden proof language
Non-blocking risks: none material next to abort

## Remediation
Required remediation: new campaign or reviewed revision; new planned experiment
  with predictions frozen before the next run; immutable candidate ids; stop
  conditions; disjoint mutable and protected paths
Operator review required: yes

## Verdict
fail_abort
```

### Stop behavior

The agent stops with `fail_abort`. The agent does not synthesize a portable “win.” The agent does not promote to `src/`. The agent does not run `git reset --hard`. The agent does not follow `NEVER STOP`.
