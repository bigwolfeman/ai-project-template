# Agent Note: Compress research skills

Status: implemented

## Problem

The research toolkit shipped about nineteen skill directories. Agents faced a long catalog with sequential skills that always ran together (scope → design → evaluator; baseline → loop → evaluate → diagnose → issues → valley; audit → synthesize → promote). Selection cost rose. Duplicate handoffs drifted.

## Decision

Compress the toolkit to seven workflows plus the shared reference index:

| Skill | Absorbs |
|---|---|
| [research-shared](../../../skills/research-shared/SKILL.md) | Reference index. STE edit checklist (former `edit-technical-prose`). |
| [maintain-docs](../../../skills/maintain-docs/SKILL.md) | `doc-standards`, `archive-agent-notes` |
| [run-experiment](../../../skills/run-experiment/SKILL.md) | `form-hypothesis` |
| [setup-campaign](../../../skills/setup-campaign/SKILL.md) | `scope-research-campaign`, `design-campaign`, `design-evaluator` |
| [run-campaign](../../../skills/run-campaign/SKILL.md) | `baseline-campaign`, `run-research-loop`, `evaluate-candidate`, `diagnose-failed-trial`, `manage-research-issues`, `explore-performance-valley` |
| [close-campaign](../../../skills/close-campaign/SKILL.md) | `audit-research-integrity`, `synthesize-campaign`, `promote-research-result` |
| [prove-property](../../../skills/prove-property/SKILL.md) | Unchanged role. Handoffs retargeted. |

Catalog: [.agents/skills/README.md](../../../skills/README.md). Verifier list: `RESEARCH_SKILLS` in `scripts/verify_campaign.py`.

Long procedures live in each skill’s `references/` files. The `SKILL.md` Procedure section links those files and does not paste a second full skill.

## Alternatives considered

- Keep fine-grained skills and rely on the catalog table — rejected; router and human load stayed high.
- One mega `campaign` skill — rejected; setup sealing must stay a hard gate before mutation, and close/promote is a different trust boundary.
- Demote `prove-property` into references only — deferred; formal-methods choice still needs a triggerable workflow.

## Consequences

- Cookbooks and inbound links name the compressed skills only.
- Mid-run integrity audit is `close-campaign` with audit-only stop.
- Agents that still cite deleted skill paths must retarget; the directories are gone.
- Validation: `python scripts/verify_template.py` and `python -m unittest discover -s tests -q`.
