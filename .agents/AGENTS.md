# AGENTS.md — Agent workspace

Read this file at least once per context window when work touches `.agents/`, skills, cookbooks, notes, or postmortems. Root standing orders live in [AGENTS.md](../AGENTS.md). Project vision lives in [docs/constitution.md](../docs/constitution.md).

## Subtrees

| Path | Job | Read next |
|---|---|---|
| [notes/](notes/AGENTS.md) | Design decisions — why, what we gave up, verification | [notes/AGENTS.md](notes/AGENTS.md) |
| [skills/](skills/AGENTS.md) | Reusable workflows — classify, setup, run, close, prove | [skills/AGENTS.md](skills/AGENTS.md) |
| [cookbook/](cookbook/AGENTS.md) | Numbered how-tos — procedure only, no rationale | [cookbook/AGENTS.md](cookbook/AGENTS.md) |
| [postmortem/](postmortem/AGENTS.md) | Incidents that escaped safeguards | [postmortem/AGENTS.md](postmortem/AGENTS.md) |

Rationale for a choice is an Agent Note or [docs/constitution.md](../docs/constitution.md). A how-to is a cookbook page. A workflow trigger is a skill.

## Planes

| Plane | Home | Holds |
|---|---|---|
| Vision | `docs/constitution.md` | What the project is and refuses to become |
| Execution | `lab/` | Spikes, campaigns, schemas, worktrees |
| Evidence | `lab/experiments/` | Hypotheses, predictions, methods, results |
| Decision | `.agents/notes/` | Agent Notes |
| Procedure | `.agents/cookbook/` | Step-by-step operator paths |
| Workflow | `.agents/skills/` | Agent procedures with triggers and handoffs |
| Incident | `.agents/postmortem/` | Escaped bugs and process gaps |
| Production | `src/` | Shipped code after human promotion |

## Glossary

Use these words consistently. Full research vocabulary: [skills/research-shared/references/terminology.md](skills/research-shared/references/terminology.md).

### Actors

| Term | Meaning |
|---|---|
| **Operator** | Human. Owns goal, budget, protected resources, evaluator acceptance, promotion. |
| **Agent** | Drafts artifacts. Mutates only manifest-authorized paths. |
| **Runner** | `scripts/run_campaign.py` and `scripts/campaign_runner/`. Isolation, ledger, disposition. |
| **Evaluator** | Protected harness that measures a candidate. |
| **Comparator** | Ranks a candidate against baseline or best. |

### Workflow kinds

| Term | Home | Meaning |
|---|---|---|
| **Spike** | `lab/spikes/` | Informal look. No prior hypothesis. |
| **Experiment** | `lab/experiments/` | One falsifiable claim. Predictions before results. |
| **Campaign** | `lab/campaigns/<slug>/` | Bounded program. Many trials. Sealed evaluator and budget. |
| **Trial** | Campaign ledger | One execution of one **candidate**. Not a hypothesis verdict. |

### Trial outcomes (candidate handling)

`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed` — never use these as hypothesis verdicts. Never use `git reset --hard` to reject a candidate.

### Hypothesis verdicts (scientific)

`supported`, `refuted`, `unresolved` — recorded in experiment files under `lab/experiments/successes/`, `mixed/`, or `refuted/`. `successes/` means predictions held past the strong bar. `mixed/` means partial signal: the idea is neither proven nor dead. `refuted/` means a solid dead end or a protocol failure (state which in Verdict). When unsure between `mixed` and `refuted`, file `mixed`.

### Artifacts

| Term | Meaning |
|---|---|
| **Agent Note** | Decision record under `.agents/notes/{lifecycle}/{class}/`. |
| **Cookbook** | How-to under `.agents/cookbook/`. |
| **Skill** | Workflow under `.agents/skills/<name>/SKILL.md`. |
| **Postmortem** | Incident write-up under `.agents/postmortem/`. |
| **Constitution** | Long-term vision in `docs/constitution.md`. |

## Classify work first

Before creating files, name the work:

1. Informal exploration → `lab/spikes/`. Stop.
2. One falsifiable claim → [run-experiment](skills/run-experiment/SKILL.md). Records in `lab/experiments/`.
3. Protected evaluator loop with budget → [setup-campaign](skills/setup-campaign/SKILL.md), then [run-campaign](skills/run-campaign/SKILL.md), then [close-campaign](skills/close-campaign/SKILL.md).
4. Design choice → Agent Note via [notes/AGENTS.md](notes/AGENTS.md).
5. Escaped systemic bug → postmortem via [postmortem/AGENTS.md](postmortem/AGENTS.md).

Do not follow unbounded loop instructions such as `NEVER STOP`.

## One home per fact

| Kind of fact | Home |
|---|---|
| Standing order | Root `AGENTS.md` |
| Vision / principles | `docs/constitution.md` |
| Why we chose X | Agent Note |
| How to do X | Cookbook |
| Measured claim | `lab/experiments/` |
| Campaign contract | `lab/campaigns/<slug>/` |
| JSON Schema | `lab/schemas/` |
| Workflow steps | Skill `SKILL.md` |
| Incident that escaped | Postmortem |

Placement detail: [docs/AGENTS.md](../docs/AGENTS.md). Documentation hygiene: [maintain-docs](skills/maintain-docs/SKILL.md).

## Validation

```text
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

A failure is an error, not a hint.
