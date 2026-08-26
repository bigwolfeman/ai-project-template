# Synthesize phase

The agent updates beliefs from campaign evidence, including negative results.

## Preconditions

Integrity audit exists with verdict `pass` or `pass_with_risks`. Campaign state is `stopped`, `completed`, or `aborted`. Ledger and linked experiments are readable.

Refuse synthesis when the audit is missing or blocking. Refuse when the campaign is still `running`. Refuse synthesis that omits negative results or that “fixes” backfilled Predictions.

## Steps

1. The agent confirms the audit verdict. If missing or blocking → stop; return to [audit.md](audit.md).
2. The agent reads `program.md`, `campaign.yaml`, the ledger, hypothesis files, and every linked experiment.
3. The agent lists every hypothesis as `supported`, `falsified`, `unresolved`, or `untested`. Trial outcomes are not hypothesis verdicts.
4. The agent includes negative results. A rejected candidate is evidence. A falsified hypothesis is evidence.
5. The agent separates facts (measurements, trial outcomes, timestamps, hardware identity) from interpretations (mechanisms, transfer claims).
6. The agent states transfer limitations. A gain on one GPU, machine, or dataset is stated as such. The agent does not claim hardware-independent improvement without evidence.
7. The agent lists unresolved issues and untested claims.
8. The agent names promotion candidates only when a candidate identifier, passing hard constraints, and a supported or still-qualified claim exist. Each candidate is `not approved` until the operator reviews it.
9. The agent recommends follow-up work with a finite next test. The agent does not recommend an unbounded loop.
10. The agent writes `reports/synthesis.md`.
11. The agent updates hypothesis state files to match the verdicts. The agent does not copy Predictions into those files.
12. The agent sets campaign projection state to `synthesized`.

## Output

```text
# Campaign synthesis
Campaign:
Evaluator lock digest:
Audit report:
Campaign state before synthesis:
Campaign state after synthesis: synthesized

## Facts
Hardware and environment:
Ledger summary:            # counts by trial outcome; do not omit rejected or crashed
Experiments included:
Negative results:

## Interpretations
Hypotheses:
- id / path / verdict (supported | falsified | unresolved | untested) / conditions

Unsupported claims:
Unresolved issues:
Transfer limitations:      # hardware, dataset, bound, model class

## Follow-up
Promotion candidates:      # candidate id, claim, not approved
Recommended next tests:    # finite
Open questions:
```

## Refusals

Omitting negative results. Treating trial `rejected` as hypothesis `falsified` (or `accepted` as `supported`) without an experiment protocol. Claiming portability when hardware identity is unknown. Writing Predictions into `program.md`. `git reset --hard`.
