# Skills

This directory owns reusable workflows. Root `AGENTS.md` names the toolkit and links here. This file selects a workflow. It does not copy a skill procedure.

Architecture: [Automated research campaigns](../notes/proposed/architecture/2026-08-24-automated-research-campaigns.md).

## Shared references

Research skills read these files. A skill body must link them. A skill body must not restate them.

| File | Subject |
|---|---|
| [terminology.md](research-shared/references/terminology.md) | Campaign terms. Trial outcomes versus hypothesis verdicts. |
| [prompt-contract.md](research-shared/references/prompt-contract.md) | Required `SKILL.md` sections. Output discipline. Untrusted logs. |
| [evidence-standard.md](research-shared/references/evidence-standard.md) | Provenance. Predictions before results. |
| [formal-methods.md](research-shared/references/formal-methods.md) | Tests, Z3, Lean. Proof documentation. |
| [ste100-style.md](research-shared/references/ste100-style.md) | Simplified Technical English principles. |

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

The agent starts with [scope-research-campaign](scope-research-campaign/SKILL.md). Campaign files live under `lab/campaigns/<slug>/`. Large artifacts live under `ignored/research/<slug>/`.

The operator owns the goal, the budget, protected resources, evaluator acceptance, and promotion. The agent must not promote campaign output into `src/` without operator review.

### Other work

A design choice is an Agent Note. Documentation placement uses [doc-standards](doc-standards/SKILL.md). An incident that escaped safeguards is a postmortem, not a campaign.

The agent must not run an unbounded loop. The agent must not use `git reset --hard` to reject a candidate.

## Shipped skills

| Skill | Purpose | Trigger | Main input | Main output |
|---|---|---|---|---|
| [archive-agent-notes](archive-agent-notes/SKILL.md) | Keep Agent Notes current. Archive superseded implemented notes. | The agent adds, audits, archives, or deletes a note. | Note path and the active note tree. | Moved or updated note. Repaired links. |
| [doc-standards](doc-standards/SKILL.md) | Place a fact in one home. Trim duplicated rules. | The agent writes, moves, or audits documentation. | The document and verifier output. | Correct placement. Passing verifier. |
| [run-experiment](run-experiment/SKILL.md) | Run one measured inquiry. Predictions first. | The agent proposes, runs, or writes up an experiment. | Question, hypothesis, predictions, method. | Planned or completed file under `docs/experiments/`. |
| [research-shared](research-shared/SKILL.md) | Shared research rules. | The agent writes or reviews research skills, campaigns, or evidence. | The current research task. | No workflow product. The agent applies the linked references. |
| [scope-research-campaign](scope-research-campaign/SKILL.md) | Classify the work. Bound the questions. | The operator requests research, a loop, or a vague investigation. | Operator goal. Constitution. Known constraints. | Classification. Scope draft. Proceed, narrow, or switch workflow. |
| [design-campaign](design-campaign/SKILL.md) | Write the operational campaign contract. | Scope is approved. The work is a campaign. | Approved scope. Linked planned experiments. | `program.md`. `campaign.yaml`. Initial state. Evaluator design request. |
| [design-evaluator](design-evaluator/SKILL.md) | Define an auditable evaluation contract. | A campaign needs measurements and comparison rules. | Campaign contract. Domain metrics. Protected inventory. | Evaluator specification. Comparator policy. Lock input. |
| [form-hypothesis](form-hypothesis/SKILL.md) | Write a falsifiable claim before execution. | The campaign needs a testable claim. | Research question. Protocol sketch. | Planned experiment document. Hypothesis state record. |
| [edit-technical-prose](edit-technical-prose/SKILL.md) | Revise technical prose with Simplified Technical English principles. | A program, report, skill, or experiment needs clearer prose. | Source document. [ste100-style.md](research-shared/references/ste100-style.md). | Revised prose. Term changes. Open ambiguities. |
| [baseline-campaign](baseline-campaign/SKILL.md) | Validate the harness before mutation. | Campaign and evaluator exist. Mutation has not started. | Campaign contract. Unchanged subject. | Baseline evidence. Ready or blocked verdict. |
| [run-research-loop](run-research-loop/SKILL.md) | Execute bounded research cycles. | Baseline is ready. Budget remains. | Current best. Issues. Remaining budget. | Trial events. Stop or continue. |
| [evaluate-candidate](evaluate-candidate/SKILL.md) | Classify evidence. Do not rewrite the hypothesis. | A trial produced evaluator output. | Evaluator result. Baseline. Comparator policy. | Comparator result. Candidate disposition. |
| [manage-research-issues](manage-research-issues/SKILL.md) | Keep persistent issue state. | A trial or diagnosis creates or updates an issue. | Issue records. Intervention history. | Updated issues. Next-test recommendation. |
| [explore-performance-valley](explore-performance-valley/SKILL.md) | Test a multi-step hypothesis that one greedy step cannot test. | One-step comparison is insufficient. | Branch budget. Safety floor. Unchanged baseline. | Branch plan. Merge, retain, or abandon. |
| [diagnose-failed-trial](diagnose-failed-trial/SKILL.md) | Classify a failed execution. | A trial crashed, was invalid, or looks like an evaluator defect. | Trial record. Logs. Evaluator lock. | Failure class. Disposition. Issue update. |
| [prove-property](prove-property/SKILL.md) | Choose the cheapest sound verification method. | A claim needs tests, Z3, or Lean. | Property. Assumptions. Model. | Proof plan and artifacts. Unproved remainder. |
| [synthesize-campaign](synthesize-campaign/SKILL.md) | Update beliefs from campaign evidence. | The campaign stops or the operator requests synthesis. | Ledger. Experiment files. Negative results. | Synthesis report. Updated verdicts. |
| [promote-research-result](promote-research-result/SKILL.md) | Move a validated result toward production. | Synthesis names a promotion candidate. | Reproduction package. Tests or proofs. | Promotion package. Agent Note. Operator review. |
| [audit-research-integrity](audit-research-integrity/SKILL.md) | Detect invalid scientific or operational practice. | Before synthesis, promotion, or on operator request. | Ledger. Predictions. Digests. | Audit verdict. Blocking findings. |

Research campaign skills follow [prompt-contract.md](research-shared/references/prompt-contract.md).

The autonomous runner is not shipped. Loop and baseline skills describe the procedure. The agent does not invent a runner.

## Ownership

- This catalog and `research-shared/` own workflow selection and shared research rules.
- Each skill directory owns its procedure.

## Validation

After the agent adds or moves notes, experiments, or docs, the agent runs:

```text
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

The verifier must pass. A failure is an error.
