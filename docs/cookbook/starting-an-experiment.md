# Starting an experiment

1. Read [docs/experiments/AGENTS.md](../experiments/AGENTS.md).
2. Follow [.agents/skills/run-experiment/SKILL.md](../../.agents/skills/run-experiment/SKILL.md).
3. Copy [docs/experiments/templates/experiment.md](../experiments/templates/experiment.md) to `docs/experiments/planned/yyyy-mm-dd-slug.md`.
4. Fill Question, Hypothesis, Predictions, Method. Commit.
5. Run `python scripts/verify_template.py`.
6. Execute the method. Write artifacts under `docs/experiments/results/yyyy-mm-dd-slug/`.
7. Fill Results, Verdict, Updated hypothesis using [experiment-completed.md](../experiments/templates/experiment-completed.md).
8. Move the file to `successes/` or `failures/`. Delete the planned copy.
9. Run the verifier again.

Do not backfill predictions.
