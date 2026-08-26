# Skills

This directory owns reusable workflows. Root `AGENTS.md` names the toolkit and links here. This file selects a workflow. It does not copy a skill procedure.

Architecture: [Automated research campaigns](../notes/implemented/architecture/2026-08-24-automated-research-campaigns.md).

## Shared references

Research skills read these files. A skill body must link them. A skill body must not restate them.

| File | Subject |
|---|---|
| [terminology.md](research-shared/references/terminology.md) | Campaign terms. Trial outcomes versus hypothesis verdicts. |
| [prompt-contract.md](research-shared/references/prompt-contract.md) | Required `SKILL.md` sections. Output discipline. Untrusted logs. |
| [evidence-standard.md](research-shared/references/evidence-standard.md) | Provenance. Predictions before results. |
| [formal-methods.md](research-shared/references/formal-methods.md) | Tests, Z3, Lean. Proof documentation. |
| [ste100-style.md](research-shared/references/ste100-style.md) | Simplified Technical English principles and edit checklist. |

Index: [research-shared/SKILL.md](research-shared/SKILL.md).

## Spike, experiment, or campaign

The agent classifies the work before it writes files.

### Spike

The operator wants an informal look. The agent has no falsifiable claim yet.

The agent works in `lab/spikes/`. The agent does not write predictions after the fact. The agent does not treat a spike as an experiment.

There is no spike skill.

### Experiment

The agent has one falsifiable claim. The agent can write predictions before any run. The work does not need a protected evaluator loop or a trial ledger.

The agent uses [run-experiment](run-experiment/SKILL.md). Records live under `docs/experiments/`.

### Campaign

The work mutates a research subject against a protected evaluator. The work needs a budget, stop conditions, or many trials. The campaign coordinates one or more experiments.

The agent starts with [setup-campaign](setup-campaign/SKILL.md). Campaign files live under `lab/campaigns/<slug>/`. Large artifacts live under `ignored/research/<slug>/`.

The operator owns the goal, the budget, protected resources, evaluator acceptance, and promotion. The agent must not promote campaign output into `src/` without operator review.

### Other work

A design choice is an Agent Note. Documentation placement uses [maintain-docs](maintain-docs/SKILL.md). An incident that escaped safeguards is a postmortem, not a campaign.

The agent must not run an unbounded loop. The agent must not use `git reset --hard` to reject a candidate.

## Shipped skills

| Skill | Purpose | Trigger | Main input | Main output |
|---|---|---|---|---|
| [research-shared](research-shared/SKILL.md) | Shared research rules. | The agent writes or reviews research skills, campaigns, or evidence. | The current research task. | No workflow product. The agent applies the linked references. |
| [maintain-docs](maintain-docs/SKILL.md) | Place facts once. Archive Agent Notes. | The agent writes or audits docs or notes. | Document or note path. Verifier output. | Correct placement. Passing verifier. |
| [run-experiment](run-experiment/SKILL.md) | One measured inquiry. Predictions first. | The agent proposes, runs, or writes up an experiment. | Question, hypothesis, predictions, method. | Planned or completed file under `docs/experiments/`. |
| [setup-campaign](setup-campaign/SKILL.md) | Classify work. Create campaign. Seal evaluator. | Research type unclear, or a campaign must be designed. | Operator goal. Constraints. Metrics. | Classification, or `program.md` / `campaign.yaml` / lock input. |
| [run-campaign](run-campaign/SKILL.md) | Baseline, trials, evaluate, diagnose, issues, valley. | Setup complete. Budget remains. | Campaign contract. Sealed lock. Candidates. | Trial events. Ready/blocked baseline. Stop or continue. |
| [close-campaign](close-campaign/SKILL.md) | Audit, synthesize, optional promote. | Campaign stopped, or operator requests audit or promotion. | Ledger. Experiments. Digests. | Audit verdict. Synthesis report. Promotion package. |
| [prove-property](prove-property/SKILL.md) | Cheapest sound verification method. | A claim needs tests, Z3, or Lean. | Property. Assumptions. Model. | Proof plan and artifacts. Unproved remainder. |

Research campaign skills (`setup-campaign`, `run-campaign`, `close-campaign`, `prove-property`) follow [prompt-contract.md](research-shared/references/prompt-contract.md).

Prose edits use the checklist in [ste100-style.md](research-shared/references/ste100-style.md). There is no separate edit-prose skill.

## Ownership

- This catalog and `research-shared/` own workflow selection and shared research rules.
- Each skill directory owns its procedure.

## Validation

After the agent adds or moves notes, experiments, or docs, the agent runs:

```text
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

The verifier must pass. A failure is an error.
