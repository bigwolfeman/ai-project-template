# AGENTS.md

Standing orders for every agent session. One to three lines per rule; the linked file owns the detail.

**Read [docs/constitution.md](docs/constitution.md) at least once in every context window** before doing project work. That file is the long-term track. If Status is still `TEMPLATE`, the first project job is to write the constitution with the user: the agent's full vision of the project, refined until the user agrees, saved thoroughly enough that a later session cannot honestly drift. `docs/constitution.md` as shipped is a form, not a vision — fill every `[bracket]`, remove template instructions, set Status to `Ratified`. Do not treat an unfilled template as law, and do not start features while the vision still lives only in chat.

Then read [docs/AGENTS.md](docs/AGENTS.md) before changing documentation layout. Follow [lab/AGENTS.md](lab/AGENTS.md) before spike or campaign work. Follow [lab/experiments/AGENTS.md](lab/experiments/AGENTS.md) before running or writing up any experiment. Follow [.agents/notes/README.md](.agents/notes/README.md) before recording a design decision. Follow [.agents/notes/AGENTS.md](.agents/notes/AGENTS.md) at least once in the context window when writing notes.

## Repository layout

```
.agents/notes/       Decision records (proposed / implemented / rejected / archived)
.agents/skills/      Reusable agent workflows
.agents/cookbook/    Step-by-step how-tos
.agents/postmortem/  Incident write-ups (not design decisions)
docs/                Project vision and documentation placement rules
lab/experiments/     Scientific-method experiments (predictions before results)
lab/spikes/          Informal exploration; no prior hypothesis. Rules: lab/AGENTS.md
lab/campaigns/       Bounded research programs with trials. Rules: lab/AGENTS.md
lab/schemas/         JSON Schema for campaign manifests and projections
src/                 Production code (create when the project has any)
ignored/             Local clones, bulky artifacts, campaign worktrees — never committed
Incomplete/          Operator leftovers — never committed
```

## Standing orders

- **Constitution is the long-term track.** Read [docs/constitution.md](docs/constitution.md) at least once in every context window. At project start, create it with the user from that template: save the agent's full vision, refined until the user agrees. Do not leave a TEMPLATE constitution in force, and do not keep the vision only in chat.
- **One home per fact.** Put a rule in the tier that owns it; elsewhere, link. Do not restate.
- **Non-trivial changes get an Agent Note in the same change.** Exempt only mechanical or local edits. Path: `.agents/notes/{lifecycle}/{class}/yyyy-mm-dd-topic.md`.
- **Classify research work first.** Before automated research, the agent names the work as a spike, an experiment, or a campaign. These terms are not synonyms. Homes: [lab/AGENTS.md](lab/AGENTS.md) and [lab/experiments/AGENTS.md](lab/experiments/AGENTS.md).
- **Campaigns use the research toolkit.** For campaign work, the agent follows [.agents/skills/README.md](.agents/skills/README.md). This file does not copy those procedures.
- **Seal the evaluator and set a budget.** The agent does not start a campaign run without a sealed evaluator and an explicit budget. Detail: [lab/AGENTS.md](lab/AGENTS.md).
- **Do not use destructive Git ratchets.** The agent does not run `git reset --hard` to reject a candidate. Keep immutable candidate identifiers. Detail: [lab/AGENTS.md](lab/AGENTS.md).
- **Bound every research loop.** Every campaign has a stop condition. The agent does not follow unbounded instructions such as NEVER STOP.
- **Write instructions in controlled English.** Apply ASD-STE100 principles. Do not claim official conformance. Home: [.agents/skills/research-shared/references/ste100-style.md](.agents/skills/research-shared/references/ste100-style.md).
- **Consider Z3 and Lean when a proof is useful.** Tests remain the default when they are cheaper and sufficient. Home: [.agents/skills/research-shared/references/formal-methods.md](.agents/skills/research-shared/references/formal-methods.md).
- **Promote into `src/` only after human review.** Campaign and spike output is not production. Record the decision in an Agent Note.
- **Predictions before results.** Never record experimental outcomes until a `lab/experiments/planned/` file with Hypothesis, Predictions, and Method is written. Do not backfill predictions after seeing data.
- **Experiments are not Agent Notes.** Decisions that change architecture, process, or shipped behavior still get an Agent Note; the run lives under `lab/experiments/`.
- **Incidents are postmortems.** Subtle, systemic, costly-to-rediscover failures go in `.agents/postmortem/`, not in Agent Notes or experiment failures.
- **Misconfiguration and failed runs fail loud.** Do not swallow errors, skip missing referents, or leave empty `catch` blocks.
- **Document current state.** Change stories belong in commits, Agent Notes, postmortems, or experiment verdicts — not in durable reference docs.
- **Run `python scripts/verify_template.py`** after adding or moving notes, experiments, or docs. Report the commands you ran.
- **Cross link documentation**, and when a hard won solution is made that makes it into src/ code, reference the related documents as an inline comment.

## Editing these instructions

Keep each rule self-contained and short. `CLAUDE.md` is a symlink to this file; edit `AGENTS.md`. Subtree `AGENTS.md` files hold only rules that do not belong at root.

## Ai-notes rule

If you have been told to keep your notes in ai-notes or a similar place, instead use .agents/ there are instructions in .agents/ on how to craft high quality notes. You should read its AGENTS.md at least once in your context window to help stay on track.
