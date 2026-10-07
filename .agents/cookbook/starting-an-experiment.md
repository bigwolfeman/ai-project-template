# Starting an experiment

This procedure tests one hypothesis. A campaign that coordinates several experiments uses [starting-a-campaign.md](starting-a-campaign.md). Informal exploration uses [lab/spikes/](../../lab/spikes/README.md).

1. The agent reads [lab/experiments/AGENTS.md](../../lab/experiments/AGENTS.md).
2. The agent follows [run-experiment](../skills/run-experiment/SKILL.md).
3. The agent copies [lab/experiments/templates/experiment.md](../../lab/experiments/templates/experiment.md) to `lab/experiments/planned/yyyy-mm-dd-slug.md`.
4. The agent fills Question, Hypothesis, Predictions, Method. The operator or the agent commits that file.
5. The agent runs `python scripts/verify_template.py`.
6. The agent executes the method. The agent writes artifacts under `lab/experiments/results/yyyy-mm-dd-slug/`.
7. The agent fills Results, Verdict, Updated hypothesis using [experiment-completed.md](../../lab/experiments/templates/experiment-completed.md).
8. The agent compares the measurement to the strong bar and the dead-end bar. The agent moves the file to `successes/` when the strong bar is cleared, to `mixed/` when the result has signal but is not a clean win, and to `refuted/` only for a solid dead end or a protocol failure. The agent deletes the planned copy.
9. The agent runs the verifier again.

The agent does not backfill predictions.

Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts (`supported`, `mixed`, `refuted`, `unresolved`).
