# Proof templates

Copy these files when a campaign or standalone claim needs a proof plan or a solver report.

Do not treat this directory as a live proof. Live reports live under `lab/campaigns/<slug>/reports/` or `docs/experiments/algorithms/`.

## When to copy

| File | Use when |
|---|---|
| [proof-plan.md](proof-plan.md) | The agent selects a verification method and records property, assumptions, model, commands, and unproved remainder. |
| [z3-report.md](z3-report.md) | The selected method is Z3 (or SMT-LIB). Copy after the proof plan names Z3. |
| [lean-report.md](lean-report.md) | The selected method is Lean. Copy after the proof plan names Lean. |

Optional offline sketches live under [examples/](examples/). Those files do not require `z3` or `lake` on `PATH`.

## Procedure and policy

1. The agent follows [.agents/skills/prove-property/SKILL.md](../../../.agents/skills/prove-property/SKILL.md).
2. The agent applies [.agents/skills/research-shared/references/formal-methods.md](../../../.agents/skills/research-shared/references/formal-methods.md).
3. The agent selects the cheapest sound method. Tests remain the default when they are cheaper and sufficient.
4. The agent does not write “proved correct” for a simplified model.
5. If `z3` or `lake` is absent, the agent sets Result to `not executed`. The agent keeps the artifact and the command.

## Validation

From the repository root:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

The verifier must exit 0. Live solver binaries are not required for that check.
