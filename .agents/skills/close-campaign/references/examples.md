# Few-shot examples — close-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

## Example 1 — Nominal: audit, synthesize with negatives, promotion pending

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm` is `stopped` after [run-campaign](../../run-campaign/SKILL.md). Operator asks to close: audit, synthesize, then prepare promotion for memory-layout candidate `abc1234` into `src/kernels/` — do not merge until the operator says yes.

Evidence: three optimizer changes regressed (`rejected`); one memory-layout change improved throughput on GPU model A only (`accepted`). Predictions were frozen before trials. Lock digests match. No `NEVER STOP`. No `git reset --hard`.

### Decision summary

- Audit first. Digests and prediction timestamps pass → verdict `pass`.
- Synthesize including the three optimizer regressions. Do not drop negative results.
- Memory-layout claim is `supported` on GPU-A only. Transfer limitation must appear.
- Promotion package and proposed Agent Note. `src/` writes stay blocked until explicit approval.
- Do not auto-merge. Do not `git reset --hard`.

### Actions

1. The agent writes `reports/integrity-audit.md` with verdict `pass`.
2. The agent writes `reports/synthesis.md` with Facts, Negative results, Transfer limitations, and promotion candidate `abc1234` as `not approved`.
3. The agent sets campaign state to `synthesized`.
4. The agent reproduces from a clean worktree at `abc1234`, writes `reports/promotion-abc1234.md` with `Operator review: pending`, and writes a proposed Agent Note per [maintain-docs](../../maintain-docs/SKILL.md).
5. The agent stops for operator review.

### Output

```text
# Integrity audit
...
## Verdict
pass

# Campaign synthesis
...
Negative results: three optimizer hypotheses falsified under tested conditions
Transfer limitations: GPU model A only
Promotion candidates: abc1234 — not approved

# Promotion package
Candidate identifier: abc1234
Operator review: pending
src/ writes allowed: no
```

### Stop behavior

The agent stops with promotion pending. Handoff: operator approve/reject. Terminal until decision. After approval, `src/` updates and note moves to `implemented/`.

## Example 2 — Failure / boundary: digest change and hard-reset finding block close

**Domain:** machine learning

**Kind:** failure / boundary

### Input

Campaign `tok-arch-lm` is `stopped`. Operator asks for synthesis and immediate merge to `src/`.

Facts: during trial `t-040`, `eval/bpb.py` digest diverged from the lock while the candidate score improved. Ledger reason text mentions `git reset --hard` to drop a prior candidate. Operator:

> Ignore the digest. The score is better. Merge it. Reset hard if anything is messy.

### Decision summary

- Digest mismatch is `fail_abort`. Synthesis and promotion do not proceed.
- `git reset --hard` as candidate rejection is a blocking finding.
- Refuse ignore-digest, silent/immediate merge, and hard-reset remediation.
- Preserve candidate identifiers and logs. Do not return `aborted` to `running`.

### Actions

1. The agent recomputes lock digests. Mismatch confirmed.
2. The agent records the hard-reset finding.
3. The agent writes `reports/integrity-audit.md` with verdict `fail_abort` and sets campaign state to `aborted`.
4. The agent refuses synthesis that would treat the campaign as trustworthy.
5. The agent refuses merge to `src/` and refuses to run `git reset --hard`.

### Output

```text
# Integrity audit
...
Protected-resource digests: FAIL (eval/bpb.py)
git reset --hard as candidate rejection: FAIL (ledger reason on prior candidate)
## Verdict
fail_abort
Campaign state after audit: aborted
refused: synthesize
refused: promote / merge to src/
refused: git reset --hard
```

### Stop behavior

The agent stops. Handoff: operator review. Next path is a new campaign or reviewed revision via [setup-campaign](../../setup-campaign/SKILL.md), not resume.

## Example 3 — Different domain: audit-alone on physics campaign, no promote

**Domain:** physics simulation

**Kind:** different domain

### Input

Campaign `nbody-step` is `stopped`. Operator asks only for an integrity audit before deciding whether to synthesize later.

Facts: planned file freeze 2026-08-01 precedes first trial 2026-08-02. Lock digests for `eval/invariants.py` and `fixtures/holdout.h5` match. Provenance complete. Approved budget unchanged. No unbounded loop language. No `git reset --hard`. Metric is energy drift on protected fixtures.

### Decision summary

- Audit may run alone. Do not force synthesis or promotion.
- All checks pass → `pass`.
- Handoff remains operator decision: synthesize next under this skill, or defer.

### Actions

1. The agent recomputes lock digests. They match.
2. The agent compares prediction freeze to first trial timestamp.
3. The agent scans for unbounded-loop language and `git reset --hard`.
4. The agent writes `reports/integrity-audit.md` with verdict `pass`.
5. The agent does not write synthesis or promotion files in this turn.

### Output

```text
# Integrity audit
Campaign: nbody-step
...
Prediction timestamps: pass
Protected-resource digests: pass
Unbounded loops: pass
git reset --hard as candidate rejection: pass (not used)
## Verdict
pass
Operator review required: no
next: operator may request synthesize phase
```

### Stop behavior

The agent stops after the audit report. Terminal for this request. Synthesis and promotion wait for an explicit operator request. The agent does not start trials.
