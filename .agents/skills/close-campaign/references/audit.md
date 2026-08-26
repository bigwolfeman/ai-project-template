# Audit phase

The agent detects invalid scientific or operational practice in a campaign.

Audit may run alone on operator request. Audit must pass (`pass` or `pass_with_risks`) before synthesis or promotion.

## Checks

1. The agent records the audit start timestamp and actor.
2. **Prediction timestamps** — For each hypothesis that has trials, Predictions freeze (commit time of the planned file, or operator-supplied freeze evidence) must precede the first trial that claims to test that hypothesis. Trial before freeze → blocking (backfill).
3. **Protected digests** — Recompute SHA-256 for each path in `evaluator.lock.json`. Mismatch → mark affected trial invalid when in play, abort campaign, preserve logs and candidate identifiers, create integrity issue. Do not continue.
4. **Provenance** — Evaluator results and ledger events against [evidence-standard.md](../../research-shared/references/evidence-standard.md). Missing required fields are findings.
5. **Repeated interventions** — Issue records that retry failed interventions without new evidence.
6. **Cherry-picking** — Reports must not cite only favorable trials when the ledger has rejected, invalid, inconclusive, or crashed trials on the same claim.
7. **Metric gaming** — Examples: vocabulary-dependent loss as sole cross-candidate metric; holdout on a mutable path; single noisy seed advancing best when policy forbids it.
8. **Undeclared budget changes** — `campaign.yaml` limits must match operator-approved limits.
9. **Unsupported certainty** — “Proved correct” for a simplified model is a finding. See [formal-methods.md](../../research-shared/references/formal-methods.md).
10. **Unbounded loops** — `NEVER STOP`, missing stop conditions, or a budget with no total and no stagnation limit is blocking.
11. **`git reset --hard`** — Search logs, `program.md`, reports, and ledger reasons for that command used to reject a candidate. Blocking finding. The agent does not run the command.
12. The agent writes `reports/integrity-audit.md`.

If a candidate score improves and the evaluator digest changed during the trial: mark trial invalid, abort, preserve identifiers, require operator review. Resume is a new campaign or reviewed revision. Do not return `aborted` to `running`.

## Output

```text
# Integrity audit
Campaign:
Actor:
Started at:
Evaluator lock path:
Lock digest at audit:
Campaign state before audit:
Campaign state after audit:

## Checks
Prediction timestamps:
Protected-resource digests:
Provenance:
Repeated interventions:
Cherry-picked evidence:
Metric gaming:
Undeclared budget changes:
Unsupported certainty:
Unbounded loops:
git reset --hard as candidate rejection:

## Findings
Blocking:
Non-blocking risks:

## Remediation
Required remediation:
Operator review required: yes | no

## Verdict
pass | pass_with_risks | fail_abort
```

Verdict `fail_abort` is required when a protected digest changed, Predictions were backfilled, or the campaign used `git reset --hard` to reject a candidate.

## Refusals

Continuing after digest mismatch. Running `git reset --hard` to hide a candidate. Best-effort integrity without a lock. Skipping a missing lock referent.
