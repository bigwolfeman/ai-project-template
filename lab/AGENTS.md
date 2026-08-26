# AGENTS.md — Lab

The lab is the execution plane. Production code lives in `src/`. Hypotheses live in [docs/experiments/](../docs/experiments/AGENTS.md). Decisions live in [.agents/notes/](../.agents/notes/README.md).

Architecture: [.agents/notes/proposed/architecture/2026-08-24-automated-research-campaigns.md](../.agents/notes/proposed/architecture/2026-08-24-automated-research-campaigns.md).

## Spikes vs campaigns

A **spike** is informal exploration. The agent places a spike in `lab/spikes/`. A spike has no prior hypothesis.

A **campaign** is a bounded research program. The agent places a campaign in `lab/campaigns/<slug>/`. A campaign coordinates one or more experiments and many **trials**.

An **experiment** is one falsifiable hypothesis. The agent records it under `docs/experiments/`. A campaign may coordinate several experiment files. The campaign `program.md` must link those files. It must not copy their predictions.

A **trial** is one execution of one **candidate**. Trial outcomes are `accepted`, `rejected`, `invalid`, `inconclusive`, and `crashed`. Those words describe candidate handling. They are not hypothesis verdicts.

The agent classifies the work before any automated research. The agent does not treat a spike as an experiment after seeing the outcome.

How-tos: [starting a campaign](../docs/cookbook/starting-a-campaign.md), [starting an experiment](../docs/cookbook/starting-an-experiment.md). Toolkit: [.agents/skills/README.md](../.agents/skills/README.md).

## Tracked vs ignored

The tracked campaign holds the contract and projections:

```
lab/campaigns/<slug>/
  program.md
  campaign.yaml
  evaluator.lock.json
  state/
  reports/
  pointers/
```

The ignored runtime holds worktrees and bulky artifacts:

```
ignored/research/<slug>/{worktrees,artifacts,logs,caches,temporary-data}/
```

The agent does not store mutable worktrees inside the tracked campaign directory. Pointers and digests stay tracked. Large files stay ignored.

Copy `lab/templates/campaign/` into `lab/campaigns/<slug>/`. If that template is absent, the agent stops and reports the missing path. Do not use the template path as a live campaign.

This repository ships no live campaigns. Copy the template to start one.

## Campaign states

States: `draft`, `ready`, `running`, `paused`, `stopped`, `completed`, `aborted`, `synthesized`, `archived`. Architecture: [Agent Note](../.agents/notes/proposed/architecture/2026-08-24-automated-research-campaigns.md).

The runner owns state transitions when a runner exists. The agent does not return a campaign from `aborted` to `running`. After an integrity failure, the operator starts a new campaign or a reviewed revision.

## Protected evaluator

The human owns the goal, the budget, protected-resource selection, evaluator acceptance, and promotion.

The evaluator lock stores content digests of protected resources. The runner verifies those digests before and after each trial. File permissions are not the only integrity check.

The agent mutates only paths listed in the campaign manifest.

The agent does not start a campaign run without a sealed evaluator and an explicit budget. This rule holds even when no runner exists yet.

The agent does not hand-write ledger events during an automated run. The ledger is execution evidence. Experiment documents summarize at hypothesis level. Detail: [docs/experiments/AGENTS.md](../docs/experiments/AGENTS.md).

## Bounds

Every campaign has a finite budget and a stop condition. The agent does not follow unbounded loop instructions such as NEVER STOP.

The agent does not run `git reset --hard` to reject a candidate. Keep immutable candidate identifiers. Advance a named best reference when the comparator accepts.

## Formal methods

When a property is cheaper to prove than to sample, the agent considers Z3 or Lean. Tests remain the default when they are cheaper and sufficient. Policy: [.agents/skills/research-shared/references/formal-methods.md](../.agents/skills/research-shared/references/formal-methods.md).

## Promotion

The agent does not promote lab work into `src/` without human review. Promotion requires tests or proofs, documentation, and an Agent Note when shipped behavior or architecture changes.
