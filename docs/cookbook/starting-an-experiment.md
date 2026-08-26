# Starting an experiment

This procedure tests one hypothesis. A campaign that coordinates several experiments uses [starting-a-campaign.md](starting-a-campaign.md). Informal exploration uses [lab/spikes/](../../lab/spikes/README.md).

1. The agent reads [docs/experiments/AGENTS.md](../experiments/AGENTS.md).
2. The agent follows [.agents/skills/run-experiment/SKILL.md](../../.agents/skills/run-experiment/SKILL.md).
3. The agent copies [docs/experiments/templates/experiment.md](../experiments/templates/experiment.md) to `docs/experiments/planned/yyyy-mm-dd-slug.md`.
4. The agent fills Question, Hypothesis, Predictions, Method. The operator or the agent commits that file.
5. The agent runs `python scripts/verify_template.py`.
6. The agent executes the method. The agent writes artifacts under `docs/experiments/results/yyyy-mm-dd-slug/`.
7. The agent fills Results, Verdict, Updated hypothesis using [experiment-completed.md](../experiments/templates/experiment-completed.md).
8. The agent moves the file to `successes/` when the hypothesis is supported. The agent moves the file to `failures/` when the hypothesis is falsified or the protocol failed. The agent deletes the planned copy.
9. The agent runs the verifier again.

The agent does not backfill predictions.

Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts (`supported`, `falsified`, `unresolved`).
