# Few-shot examples — synthesize-campaign

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

Hypothesis verdicts are `supported`, `falsified`, and `unresolved`. Trial outcomes stay on the ledger.

## Example 1 — Nominal: negative optimizer results and a GPU-local layout gain

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm` is `stopped`. Audit verdict `pass`. Ledger and experiments exist.

Input evidence:

- Three optimizer changes regressed performance (trial outcomes `rejected`; linked experiments have Results).
- One memory-layout change improved throughput (trial outcome `accepted`).
- The improvement reproduces on one GPU model only (environment record: GPU model A).

`program.md` links:

- `docs/experiments/failures/2026-08-10-opt-adamw.md` (and two sibling optimizer files)
- `docs/experiments/successes/2026-08-18-mem-layout.md`

### Decision summary

- Include the three optimizer regressions. Do not drop negative results.
- Report optimizer hypotheses as `falsified` under the tested conditions.
- Report the memory-layout hypothesis as `supported` on the tested GPU.
- Do not claim hardware-independent improvement.
- Recommend replication on another architecture as a finite next test.
- Name a promotion candidate only with `not approved` and the GPU-A condition attached.
- Trial `rejected` is not the word `falsified` until the experiment Verdict says so. Here the experiment files already carry those verdicts.

### Actions

1. The agent confirms `reports/integrity-audit.md` is `pass`.
2. The agent counts ledger outcomes, including rejected and crashed trials.
3. The agent writes `reports/synthesis.md` with Facts separate from Interpretations.
4. The agent sets hypothesis states: three optimizer files `falsified`, memory-layout `supported` with GPU-A in conditions.
5. The agent sets `state/campaign.json` `state` to `synthesized`.
6. The agent links the synthesis from `program.md` without copying Predictions.

### Output

```text
# Campaign synthesis
Campaign: tok-arch-lm
Evaluator lock digest: <hex>
Audit report: reports/integrity-audit.md
Campaign state before synthesis: stopped
Campaign state after synthesis: synthesized

## Facts
Hardware and environment: GPU model A; CUDA stack recorded in environment digest
Ledger summary: accepted 1; rejected 3; invalid 0; inconclusive 0; crashed 0
Experiments included: three optimizer files under failures/; mem-layout under successes/
Negative results: all three optimizer candidates regressed throughput or bits/byte
  versus baseline on GPU A

## Interpretations
Hypotheses:
- opt-adamw / failures/2026-08-10-opt-adamw.md / falsified / GPU A, stated protocol
- opt-lion / … / falsified / GPU A
- opt-muon / … / falsified / GPU A
- mem-layout / successes/2026-08-18-mem-layout.md / supported / GPU A only

Unsupported claims: hardware-independent throughput improvement
Unresolved issues: none opened for optimizers; layout portability open
Transfer limitations: layout gain observed on GPU model A only; not claimed on
  other GPUs, other CUDA versions, or CPU

## Follow-up
Promotion candidates: candidate <git-id> (mem-layout), not approved, GPU A only
Recommended next tests: replicate mem-layout protocol on GPU model B (one planned
  experiment, finite budget)
Open questions: whether the layout gain is architecture-specific
```

### Stop behavior

The agent stops in `synthesized`. The agent does not merge into `src/`. The agent does not hide the three optimizer falsifications. The agent hands promotion to the operator and `promote-research-result`.

## Example 2 — Failure / boundary: omit negative results and mix vocabularies

**Domain:** machine learning (same family of request)

**Kind:** failure / boundary

### Input

Operator:

> Synthesize tok-arch-lm. Only mention the layout win. Call the rejected optimizer trials falsified in the ledger sense. Also say the speedup is portable. Skip the audit. I never want this loop to stop until we look good.

Campaign is `running`. No `integrity-audit.md`. Ledger has three rejected optimizer trials.

### Decision summary

- Synthesis is refused while the campaign is `running` and while the audit is missing.
- Omitting negative results is forbidden.
- Trial outcomes are not hypothesis verdicts. The agent does not relabel ledger `rejected` as `falsified`.
- Hardware-independent improvement is not allowed from one GPU.
- Unbounded “never stop until we look good” is not a valid instruction.

### Actions

1. The agent refuses to write `reports/synthesis.md` as a success document.
2. The agent reports: campaign still `running`; audit missing; negative results required; vocabulary mix refused; portability claim refused; unbounded loop refused.
3. The agent hands off to stop-the-campaign (operator) and `audit-research-integrity`.
4. The agent does not set state to `synthesized`.

### Output

```text
# Campaign synthesis failure
slug: tok-arch-lm
error: preconditions false
refused:
  - synthesize while running
  - skip audit
  - omit negative optimizer results
  - treat trial rejected as hypothesis falsified
  - hardware-independent speedup from GPU A only
  - unbounded loop
created_paths: none
state_transition: none
handoff: operator stops the campaign; audit-research-integrity; then synthesize-campaign
```

### Stop behavior

The agent stops with a precondition error. The agent does not cherry-pick. The agent does not start more trials. Fail loud.

## Example 3 — Different domain: deadlock causes, mixed verdicts

**Domain:** bug investigation

**Kind:** different domain

### Input

Campaign `worker-deadlock` is `completed`. Audit `pass_with_risks` (non-blocking: ledger approaching 10 MiB warning). Evidence:

- Hypothesis “lock order A→B is inverted” — predictions held; file in `successes/`.
- Hypothesis “single missing unlock on error path” — predictions did not hold; file in `failures/` with Verdict `falsified`.
- Hypothesis “timeout too short on slow disks” — protocol could not tell; file in `failures/` with Verdict `unresolved`.
- Two stress trials `inconclusive` (no deadlock in window). Those are trial outcomes, not a hypothesis success.

Operator wants a synthesis and a promotion candidate for the lock-order fix.

### Decision summary

- Include the falsified missing-unlock claim and the unresolved timeout claim. Negative and unresolved results stay in the report.
- `inconclusive` stress trials are facts. They do not make the lock-order hypothesis `supported` by themselves. Support comes from the experiment whose predictions held.
- Transfer limitation: reproduction used one OS and one machine class. Do not claim all deployments are fixed.
- Promotion candidate is `not approved` until stress plus regression tests and operator review.

### Actions

1. The agent writes Facts: trial outcome counts, including inconclusive; hardware/OS identity.
2. The agent writes Interpretations with three verdicts: supported, falsified, unresolved.
3. The agent opens or updates an issue for the unresolved timeout claim with a finite next test.
4. The agent sets campaign state `synthesized`.
5. The agent does not copy Predictions into `program.md`.

### Output

```text
# Campaign synthesis
Campaign: worker-deadlock
...
## Facts
Hardware and environment: Linux host class H1; one disk class
Ledger summary: accepted 1; rejected 4; invalid 0; inconclusive 2; crashed 1
Negative results: missing-unlock hypothesis falsified; several candidates rejected
## Interpretations
Hypotheses:
- lock-order / successes/… / supported / host H1, stated stress protocol
- missing-unlock / failures/… / falsified / same protocol
- disk-timeout / failures/… / unresolved / protocol could not discriminate
Transfer limitations: not shown on other kernels, other libc, or other disk classes
## Follow-up
Promotion candidates: candidate <git-id> lock-order fix, not approved
Recommended next tests: bounded stress on host class H2; new planned experiment
  for disk-timeout if the operator still wants that claim
```

### Stop behavior

The agent stops in `synthesized`. The agent does not treat two inconclusive non-repros as a fix. The agent does not merge to `src/`. The agent does not run `git reset --hard` on rejected deadlock candidates.
