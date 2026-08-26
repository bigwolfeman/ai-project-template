# Agent Note: Automated research campaigns in lab/

Status: proposed

## Problem

`lab/` is only unstructured spikes. `docs/experiments/` records one hypothesis at a time. Neither supports a bounded, metric-gated campaign that mutates a subject, evaluates it against a protected harness, and keeps rejected work as evidence. Agents therefore mix spikes, experiments, and production edits, or they invent unbounded loops with destructive Git resets.

This note extends [the template-structure note](../../implemented/process/2026-08-20-template-structure-from-harness.md). It does not replace experiment documents or Agent Notes.

## Proposal

Add a domain-general research model:

- **Spike** — informal exploration in `lab/spikes/`. No prior hypothesis.
- **Experiment** — one falsifiable hypothesis in `docs/experiments/`.
- **Campaign** — a bounded program in `lab/campaigns/<slug>/` that coordinates one or more experiments and many **trials**.
- **Trial** — one execution of one **candidate**. Outcomes: `accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`. These are not hypothesis verdicts.
- **Hypothesis verdicts** — `supported`, `falsified`, `unresolved`. Keep experiment folders `planned/`, `successes/`, and `failures/` in this slice. `successes/` means predictions held. `failures/` means falsified or protocol failure. State which in Verdict.

`lab/` is the execution plane. `docs/experiments/` is the evidence plane. `.agents/notes/` is the decision plane. `src/` receives promoted work only after human review.

### Campaign files

Tracked campaign:

```
lab/campaigns/<slug>/
  program.md              Human-owned intent; links experiments; does not copy predictions
  campaign.yaml           Machine-readable contract
  evaluator.lock.json     Digests of protected resources
  state/                  Projections rebuilt from the ledger
  reports/                Human summaries
  pointers/               Digests and paths into ignored artifacts
```

Ignored runtime:

```
ignored/research/<slug>/{worktrees,artifacts,logs,caches,temporary-data}/
```

Templates live in `lab/templates/campaign/`. Copy them. Do not use the template path as a live campaign.

### Trust boundaries

- Humans own goal, budget, protected resources, evaluator acceptance, and promotion.
- Agents mutate only paths listed in the manifest.
- The evaluator lock is verified before and after each trial. File permissions are not the only integrity check.
- The runner owns isolation, timeouts, ledger append, and candidate disposition. Agents do not hand-write ledger events during an automated run.
- Do not use `git reset --hard` to reject candidates. Keep immutable candidate identifiers. Advance a named best reference when the comparator accepts.

### Resolved defaults for this slice

- Ledgers are compact JSONL and are committed. Large artifacts stay in `ignored/`.
- Rejected code candidates keep Git commit IDs in the ledger. Optional refs come later.
- First runner uses Git worktrees under `ignored/research/<slug>/worktrees/` and a restricted subprocess, not containers. CLI entry is `scripts/run_campaign.py` with subcommands `validate`, `baseline`, `trial`, and `status`.
- JSON Schema is Draft 2020-12. The verifier rejects unknown fields.
- First comparator: hard constraints, then declared objectives, then mean/stddev with an equivalence margin. Complexity is an explicit hard limit, lexicographic tie-break, weighted objective, or human-review item.
- Prompt tests are deterministic rule checks.
- ASD-STE100: apply its principles. Do not copy licensed issue lists. Do not claim official conformance.
- Z3 and Lean are optional tools. Tests remain the default when they are cheaper and sufficient. Proof report templates live under `lab/templates/proofs/`.
- Warn when a tracked ledger exceeds 10 MiB. Compact only after synthesis.
- External instruments need an attestation file: time, operator, instrument identity, and a digest of the recorded data.

### Toolkit

Workflows live under `.agents/skills/`. Catalog: [.agents/skills/README.md](../../../.agents/skills/README.md). Root `AGENTS.md` names the toolkit and links. It does not copy procedures.

**Shipped:** campaign skills from scope through audit and promotion (`scope-research-campaign`, `design-campaign`, `design-evaluator`, `form-hypothesis`, `baseline-campaign`, `run-research-loop`, `evaluate-candidate`, `manage-research-issues`, `explore-performance-valley`, `diagnose-failed-trial`, `prove-property`, `synthesize-campaign`, `promote-research-result`, `audit-research-integrity`, plus `research-shared`, `edit-technical-prose`, `run-experiment`, `doc-standards`, `archive-agent-notes`). Campaign static contract: `lab/templates/campaign/`, schemas under `schemas/`, `scripts/verify_campaign.py`. Proof templates: `lab/templates/proofs/`. Cookbook: [docs/cookbook/starting-a-campaign.md](../../../docs/cookbook/starting-a-campaign.md), [docs/cookbook/running-a-campaign.md](../../../docs/cookbook/running-a-campaign.md).

**Runner status:** Wave 3 builds `scripts/campaign_runner/` and `scripts/run_campaign.py`. Until that CLI is present and passing its gates, loop and baseline skills describe the procedure only. The agent does not invent a runner. The agent does not run `git reset --hard` to reject a candidate.

## Alternatives considered

- **Keep `lab/` as spikes only** — agents still have nowhere to put protected evaluators, budgets, or trial ledgers.
- **Treat every trial as an experiment Markdown file** — hundreds of files, and the scientific record mixes with execution noise.
- **Copy Karpathy autoresearch (`program.md` + mutable `train.py` + `git reset`)** — ML-specific, destructive, unbounded, and evaluator “read-only” is not a real boundary.
- **Neutral `completed/` instead of `successes/`/`failures/`** — clearer scientifically; deferred so this slice does not break the existing experiment verifier.
- **ADAS-style meta-agent archive as the first artifact** — too large; campaigns and evaluators must exist first.

## Acceptance criteria

- Root and `lab/` docs distinguish spike, experiment, campaign, and trial.
- `lab/templates/campaign/` validates as a campaign.
- `python scripts/verify_template.py` checks campaign layout, schemas, and the research skills.
- No workflow instructs `git reset --hard` to reject a candidate.
- No standing order uses an unbounded “never stop” loop.
- Each shipped research skill has three few-shot examples.
- Proof templates exist under `lab/templates/proofs/` with required documentation fields.
- Cookbook covers starting and running a campaign without inventing a runner when the CLI is absent.
- Runner CLI (`scripts/run_campaign.py`) validates, baselines, and trials a campaign without destructive Git resets — **open until Wave 3 runner gates pass**.

## Risks

- Agents may treat a campaign as production. Mitigation: promotion requires human review and an Agent Note.
- Compact ledgers may still grow large. Mitigation: 10 MiB warning and post-synthesis archival.
- Keeping `successes/`/`failures/` can confuse trial outcomes with hypothesis verdicts. Mitigation: explicit vocabulary in `docs/experiments/AGENTS.md` and skill prompts.
