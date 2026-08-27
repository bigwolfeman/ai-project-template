# Running a campaign

This procedure executes a campaign after [starting-a-campaign.md](starting-a-campaign.md) is complete. Skill catalog: [.agents/skills/README.md](../skills/README.md). Lab rules: [lab/AGENTS.md](../../lab/AGENTS.md).

## Preconditions

1. The work is classified as a campaign. If the work is a spike or one experiment, stop. Use [lab/spikes/](../../lab/spikes/README.md) or [starting-an-experiment.md](starting-an-experiment.md).
2. `lab/campaigns/<slug>/` exists. The agent copied it from `lab/templates/campaign/`.
3. A planned experiment file exists under `lab/experiments/planned/`. `program.md` links that file. `program.md` does not copy predictions.
4. The evaluator is sealed (`evaluator.lock.json`). The budget is explicit in `campaign.yaml`.
5. The agent does not invent a runner. If `scripts/run_campaign.py` is absent, the agent follows [run-campaign](../skills/run-campaign/SKILL.md) as procedure only. The agent stops and reports the missing CLI when the operator asked for CLI steps.

## Procedure

1. **Set up.** The agent follows [setup-campaign](../skills/setup-campaign/SKILL.md) until classification, campaign files, and evaluator lock input match the operator goal.
2. **Form hypothesis.** The agent follows [run-experiment](../skills/run-experiment/SKILL.md) for the planned file. Predictions stay in `lab/experiments/planned/`.
3. **Seal evaluator.** The operator accepts `evaluator.lock.json`. The agent does not start trials without a sealed evaluator and a budget.
4. **Validate the campaign.** From the repository root:

   ```bash
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py validate lab/campaigns/<slug>
   ```

   If that command is missing, the agent runs `env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py` and reports that the campaign runner CLI is not shipped. The agent does not invent a substitute runner.
5. **Baseline and trials.** The agent follows [run-campaign](../skills/run-campaign/SKILL.md):

   ```bash
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py baseline lab/campaigns/<slug>
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py trial lab/campaigns/<slug>
   ```

   The agent does not run `git reset --hard` to reject a candidate. The agent keeps immutable candidate identifiers. The agent does not follow unbounded instructions such as NEVER STOP.
6. **Close.** When a stop condition fires, or when the operator requests synthesis or promotion, the agent follows [close-campaign](../skills/close-campaign/SKILL.md). Promotion into `src/` requires operator review and an Agent Note when shipped behavior or architecture changes.

## Hard rules

- Bounded budgets only. Wall-clock, trial count, and stagnation limits in the manifest are stop conditions.
- No `git reset --hard` to reject a candidate.
- No invented runner when `scripts/run_campaign.py` is missing.
- Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts (`supported`, `falsified`, `unresolved`).
- Formal claims use [prove-property](../skills/prove-property/SKILL.md) and [lab/templates/proofs/](../../lab/templates/proofs/README.md).

## Status check

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py status lab/campaigns/<slug>
```

Use this command when the CLI exists. Otherwise inspect `lab/campaigns/<slug>/state/` and the ledger pointer files.

## Related

- [Starting a campaign](starting-a-campaign.md)
- [Starting an experiment](starting-an-experiment.md)
- Architecture: [.agents/notes/implemented/architecture/2026-08-24-automated-research-campaigns.md](../notes/implemented/architecture/2026-08-24-automated-research-campaigns.md)
