# AGENTS.md — Lab

The lab is the execution plane. Production code lives in `src/`. Hypotheses live in [lab/experiments/](experiments/AGENTS.md). Decisions live in [.agents/notes/](../.agents/notes/AGENTS.md).

Architecture: [.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md](../.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md).

## Spikes vs campaigns

A **spike** is informal exploration. The agent places a spike in `lab/spikes/`. A spike has no prior hypothesis.

A **campaign** is a bounded research program. The agent places a campaign in `lab/campaigns/<slug>/`. A campaign coordinates one or more experiments and many **trials**.

An **experiment** is one falsifiable hypothesis. The agent records it under `lab/experiments/`. A campaign may coordinate several experiment files. The campaign `program.md` must link those files. It must not copy their predictions.

A **trial** is one execution of one **candidate**. Trial outcomes are `accepted`, `rejected`, `invalid`, `inconclusive`, and `crashed`. Those words describe candidate handling. They are not hypothesis verdicts.

The agent classifies the work before any automated research. The agent does not treat a spike as an experiment after seeing the outcome.

How-tos: [starting a campaign](../.agents/cookbook/starting-a-campaign.md), [starting an experiment](../.agents/cookbook/starting-an-experiment.md). Toolkit: [.agents/skills/AGENTS.md](../.agents/skills/AGENTS.md).

## Literate lab

Documentation lives with the code. The lab is where ideas start, so the lab is where the idea gets written down first.

- A spike opens with a pseudocode block (a header comment or a `NOTES.md` beside the code) that states what the spike tries. The agent writes it before the code and fixes it when the code changes.
- An experiment's Method holds pseudocode of the change under test. `scripts/verify_template.py` checks for the fenced block.
- An algorithm writeup holds the full pseudocode in Sketch. Code that implements it carries a comment with a relative link back to the writeup.
- A campaign `program.md` states the mutable subject's intended behavior in pseudocode. Each accepted candidate keeps a short pseudocode diff in its report.
- Promotion into `src/` carries the pseudocode along as the module or function docstring, plus links to the experiment and the Agent Note. A reader of `src/` sees why the code exists without leaving the file.

Pseudocode is not prose about the code. It is the algorithm in short, readable steps, with the same control flow as the code. When code and pseudocode disagree, one of them is a bug. Fix it in the same change.

Agent Notes stay under `.agents/notes/`. They hold decisions and rejected alternatives, which are too long and too raw to sit beside code. The code links to them.

## Names, not codes

The agent gives every spike, experiment, ablation, arm, and task a descriptive name of 2 to 5 words. Letter-number codes (`V1`, `S16`) may follow a name as an alias. They never replace it. A campaign `program.md` lists its arms and tasks by name. Detail: [experiments/AGENTS.md](experiments/AGENTS.md).

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

JSON Schema for manifests, locks, ledger events, and state projections lives in `lab/schemas/`. `scripts/verify_campaign.py` and `scripts/campaign_schema.py` validate against those files.

This repository ships no live campaigns. Copy the template to start one.

## Campaign states

States: `draft`, `ready`, `running`, `paused`, `stopped`, `completed`, `aborted`, `synthesized`, `archived`. Architecture: [Agent Note](../.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md).

The runner owns state transitions when a runner exists. The agent does not return a campaign from `aborted` to `running`. After an integrity failure, the operator starts a new campaign or a reviewed revision.

## Protected evaluator

The human owns the goal, the budget, protected-resource selection, evaluator acceptance, and promotion.

The evaluator lock stores content digests of protected resources. The runner verifies those digests before and after each trial. File permissions are not the only integrity check.

The agent mutates only paths listed in the campaign manifest.

The agent does not start a campaign run without a sealed evaluator and an explicit budget. This rule holds even when no runner exists yet.

The agent does not hand-write ledger events during an automated run. The ledger is execution evidence. Experiment documents summarize at hypothesis level. Detail: [lab/experiments/AGENTS.md](../lab/experiments/AGENTS.md).

## Bounds

Every campaign has a finite budget and a stop condition. The agent does not follow unbounded loop instructions such as NEVER STOP.

The agent does not run `git reset --hard` to reject a candidate. Keep immutable candidate identifiers. Advance a named best reference when the comparator accepts.

## Formal methods

When a property is cheaper to prove than to sample, the agent considers Z3 or Lean. Tests remain the default when they are cheaper and sufficient. Policy: [.agents/skills/research-shared/references/formal-methods.md](../.agents/skills/research-shared/references/formal-methods.md).

## Promotion

The agent does not promote lab work into `src/` without human review. Promotion requires tests or proofs, documentation, and an Agent Note when shipped behavior or architecture changes.
