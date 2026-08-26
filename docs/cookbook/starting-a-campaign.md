# Starting a campaign

A campaign is a bounded research program. It is not a spike. It is not one experiment.

1. The agent reads [lab/AGENTS.md](../../lab/AGENTS.md).
2. The agent classifies the work. If the work is informal exploration, the agent stops and uses [lab/spikes/](../../lab/spikes/README.md). If the work is one hypothesis, the agent stops and uses [starting-an-experiment.md](starting-an-experiment.md).
3. The agent follows the research toolkit at [.agents/skills/README.md](../../.agents/skills/README.md). If that catalog is absent, the agent stops and reports the missing path.
4. The human owns the goal, the budget, protected resources, evaluator acceptance, and promotion. The agent may draft those items. The agent does not silently approve material cost or irreversible change.
5. The agent copies `lab/templates/campaign/` to `lab/campaigns/<slug>/`. If that template is absent, the agent stops and reports the missing path. The agent does not use the template path as a live campaign.
6. The agent writes `program.md`. That file links planned experiment documents. It does not copy their predictions. Experiment procedure: [starting-an-experiment.md](starting-an-experiment.md).
7. The agent and the human seal the evaluator (`evaluator.lock.json`) and set an explicit budget before any run.
8. After the campaign is sealed, the agent follows [running-a-campaign.md](running-a-campaign.md). If `scripts/run_campaign.py` is absent, the agent uses [run-campaign](../../.agents/skills/run-campaign/SKILL.md) as procedure only. The agent does not invent a runner.
9. The agent does not run `git reset --hard` to reject a candidate. The agent does not follow unbounded loop instructions such as NEVER STOP.
10. The agent does not promote campaign output into `src/` without human review and an Agent Note.

Trial outcomes are `accepted`, `rejected`, `invalid`, `inconclusive`, and `crashed`. Hypothesis verdicts are `supported`, `falsified`, and `unresolved`. Do not mix these vocabularies.
