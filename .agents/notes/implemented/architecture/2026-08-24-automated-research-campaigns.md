# Agent Note: Automated research campaigns in lab/

Status: implemented

## Problem

`lab/` was only unstructured spikes. `docs/experiments/` records one hypothesis at a time. Neither supported a bounded, metric-gated campaign that mutates a subject, evaluates it against a protected harness, and keeps rejected work as evidence. Agents mixed spikes, experiments, and production edits, or invented unbounded loops with destructive Git resets.

This note extends [the template-structure note](../../implemented/process/2026-08-20-template-structure-from-harness.md). It does not replace experiment documents or Agent Notes.

## Decision

The repository uses a domain-general research model:

- **Spike** — informal exploration in `lab/spikes/`. No prior hypothesis.
- **Experiment** — one falsifiable hypothesis in `docs/experiments/`.
- **Campaign** — a bounded program in `lab/campaigns/<slug>/` that coordinates one or more experiments and many **trials**.
- **Trial** — one execution of one **candidate**. Outcomes: `accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`. These are not hypothesis verdicts.
- **Hypothesis verdicts** — `supported`, `falsified`, `unresolved`. Experiment folders remain `planned/`, `successes/`, and `failures/`. `successes/` means predictions held. `failures/` means falsified or protocol failure. State which in Verdict.

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

When `branch_worktree_policy.isolation` is `git_worktree`, the runner creates a disposable worktree under `ignored/research/<slug>/worktrees/`, overlays `mutable_paths` and `protected_paths` from the campaign directory into that worktree, and runs the evaluator with `cwd` set to the worktree. Lock digests are still verified against the campaign directory. The runner never uses `git reset --hard`.

### Trust boundaries

- Humans own goal, budget, protected resources, evaluator acceptance, and promotion.
- Agents mutate only paths listed in the manifest.
- The evaluator lock is verified before and after each trial. File permissions are not the only integrity check.
- The runner owns isolation, timeouts, ledger append, and candidate disposition. Agents do not hand-write ledger events during an automated run.
- Rejected candidates keep immutable identifiers. A named best reference advances when the comparator accepts.

### Defaults in force

- Ledgers are compact JSONL and are committed. Large artifacts stay in `ignored/`.
- First runner uses Git worktrees and a restricted subprocess. CLI: `scripts/run_campaign.py` with `validate`, `baseline`, `trial`, and `status`.
- Optional manifest field `adapter` selects a registered adapter (`generic_command`, `pytest_benchmark`, `prompt_eval`). Default is `generic_command`.
- JSON Schema is Draft 2020-12. The verifier rejects unknown fields.
- Comparator: hard constraints, then objectives, then mean/stddev with an equivalence margin.
- Prompt tests are deterministic rule checks under `tests/prompt_fixtures/`.
- ASD-STE100 principles apply to instructions and reports. The project does not claim official conformance.
- Z3 and Lean are optional. Proof templates live under `lab/templates/proofs/`. CI may skip live solvers when they are absent.

### Toolkit

Workflows live under `.agents/skills/`. Catalog: [.agents/skills/README.md](../../../.agents/skills/README.md). Root `AGENTS.md` names the toolkit and links. It does not copy procedures.

Shipped campaign skills run from scope through audit and promotion. Campaign static contract: `lab/templates/campaign/`, schemas under `schemas/`, `scripts/verify_campaign.py`. Runner: `scripts/campaign_runner/`, `scripts/run_campaign.py`. Cookbook: [docs/cookbook/starting-a-campaign.md](../../../docs/cookbook/starting-a-campaign.md), [docs/cookbook/running-a-campaign.md](../../../docs/cookbook/running-a-campaign.md).

## Alternatives considered

- **Keep `lab/` as spikes only** — agents still have nowhere to put protected evaluators, budgets, or trial ledgers.
- **Treat every trial as an experiment Markdown file** — hundreds of files, and the scientific record mixes with execution noise.
- **Copy Karpathy autoresearch (`program.md` + mutable `train.py` + `git reset`)** — ML-specific, destructive, unbounded, and evaluator “read-only” is not a real boundary.
- **Neutral `completed/` instead of `successes/`/`failures/`** — clearer scientifically; deferred so the existing experiment verifier stays stable.
- **ADAS-style meta-agent archive as the first artifact** — too large; campaigns and evaluators must exist first.

## Consequences

- Agents classify work as spike, experiment, or campaign before automated research.
- A campaign cannot run without a sealed evaluator lock and an explicit budget.
- Disposable worktrees keep the production branch unchanged. Mutable and protected paths are overlaid into the worktree for evaluation.
- Negative trial evidence remains in the ledger. Promotion into `src/` requires human review and an Agent Note.
- Keeping `successes/`/`failures/` can confuse trial outcomes with hypothesis verdicts. Skills and `docs/experiments/AGENTS.md` keep the vocabularies separate.
- Verification: `python scripts/verify_template.py`, `python scripts/verify_campaign.py lab/templates/campaign`, and `python -m unittest discover -s tests -q`.
