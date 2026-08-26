# Running a campaign

This procedure executes a campaign after [starting-a-campaign.md](starting-a-campaign.md) is complete. Skill catalog: [.agents/skills/README.md](../../.agents/skills/README.md). Lab rules: [lab/AGENTS.md](../../lab/AGENTS.md).

## Preconditions

1. The work is classified as a campaign. If the work is a spike or one experiment, stop. Use [lab/spikes/](../../lab/spikes/README.md) or [starting-an-experiment.md](starting-an-experiment.md).
2. `lab/campaigns/<slug>/` exists. The agent copied it from `lab/templates/campaign/`.
3. A planned experiment file exists under `docs/experiments/planned/`. `program.md` links that file. `program.md` does not copy predictions.
4. The evaluator is sealed (`evaluator.lock.json`). The budget is explicit in `campaign.yaml`.
5. The agent does not invent a runner. If `scripts/run_campaign.py` is absent, the agent follows [baseline-campaign](../../.agents/skills/baseline-campaign/SKILL.md) and [run-research-loop](../../.agents/skills/run-research-loop/SKILL.md) as procedures only. The agent stops and reports the missing CLI when the operator asked for CLI steps.

## Procedure

1. **Classify.** The agent follows [scope-research-campaign](../../.agents/skills/scope-research-campaign/SKILL.md). The agent confirms the work remains a campaign.
2. **Design.** The agent follows [design-campaign](../../.agents/skills/design-campaign/SKILL.md) until `program.md` and `campaign.yaml` match the operator goal.
3. **Form hypothesis.** The agent follows [form-hypothesis](../../.agents/skills/form-hypothesis/SKILL.md). Predictions stay in the planned experiment file.
4. **Seal evaluator.** The agent follows [design-evaluator](../../.agents/skills/design-evaluator/SKILL.md). The operator accepts the lock. The agent does not start trials without a sealed evaluator and a budget.
5. **Validate the campaign.** From the repository root:

   ```bash
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py validate lab/campaigns/<slug>
   ```

   If that command is missing, the agent runs `env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py` and reports that the campaign runner CLI is not shipped. The agent does not invent a substitute runner.
6. **Baseline.** The agent measures the unchanged subject:

   ```bash
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py baseline lab/campaigns/<slug>
   ```

   Skill procedure: [baseline-campaign](../../.agents/skills/baseline-campaign/SKILL.md). The agent stops when the baseline is blocked.
7. **Trial.** While budget remains and no stop condition fires:

   ```bash
   env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py trial lab/campaigns/<slug>
   ```

   Skill procedure: [run-research-loop](../../.agents/skills/run-research-loop/SKILL.md). The agent does not run `git reset --hard` to reject a candidate. The agent keeps immutable candidate identifiers. The agent does not follow unbounded instructions such as NEVER STOP.
8. **Evaluate.** After each trial result, the agent follows [evaluate-candidate](../../.agents/skills/evaluate-candidate/SKILL.md). Crashes and invalid results use [diagnose-failed-trial](../../.agents/skills/diagnose-failed-trial/SKILL.md). Persistent defects use [manage-research-issues](../../.agents/skills/manage-research-issues/SKILL.md).
9. **Synthesize.** When a stop condition fires, or when the operator requests synthesis, the agent follows [audit-research-integrity](../../.agents/skills/audit-research-integrity/SKILL.md), then [synthesize-campaign](../../.agents/skills/synthesize-campaign/SKILL.md).
10. **Promote.** Promotion into `src/` requires operator review. The agent follows [promote-research-result](../../.agents/skills/promote-research-result/SKILL.md). The agent does not promote without an Agent Note when shipped behavior or architecture changes.

## Hard rules

- Bounded budgets only. Wall-clock, trial count, and stagnation limits in the manifest are stop conditions.
- No `git reset --hard` to reject a candidate.
- No invented runner when `scripts/run_campaign.py` is missing.
- Trial outcomes (`accepted`, `rejected`, `invalid`, `inconclusive`, `crashed`) are not hypothesis verdicts (`supported`, `falsified`, `unresolved`).
- Formal claims use [prove-property](../../.agents/skills/prove-property/SKILL.md) and [lab/templates/proofs/](../../lab/templates/proofs/README.md).

## Status check

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/run_campaign.py status lab/campaigns/<slug>
```

Use this command when the CLI exists. Otherwise inspect `lab/campaigns/<slug>/state/` and the ledger pointer files.

## Related

- [Starting a campaign](starting-a-campaign.md)
- [Starting an experiment](starting-an-experiment.md)
- Architecture proposal: [.agents/notes/proposed/architecture/2026-08-24-automated-research-campaigns.md](../../.agents/notes/proposed/architecture/2026-08-24-automated-research-campaigns.md)
