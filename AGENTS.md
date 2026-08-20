# AGENTS.md

Standing orders for every agent session. One to three lines per rule; the linked file owns the detail.

**Read [docs/constitution.md](docs/constitution.md) at least once in every context window** before doing project work. That file is the long-term track. If Status is still `TEMPLATE`, the first project job is to write the constitution with the user: the agent's full vision of the project, refined until the user agrees, saved thoroughly enough that a later session cannot honestly drift. `docs/constitution.md` as shipped is a form, not a vision — fill every `[bracket]`, remove template instructions, set Status to `Ratified`. Do not treat an unfilled template as law, and do not start features while the vision still lives only in chat.

Then read [docs/AGENTS.md](docs/AGENTS.md) before changing documentation layout. Follow [docs/experiments/AGENTS.md](docs/experiments/AGENTS.md) before running or writing up any experiment. Follow [.agents/notes/README.md](.agents/notes/README.md) before recording a design decision. Follow [.agents/notes/AGENTS.md](.agents/notes/AGENTS.md) at least once in the context window when writing notes.

## Repository layout

```
.agents/notes/     Decision records (proposed / implemented / rejected / archived)
.agents/skills/    Reusable agent workflows
docs/              Human-facing docs; subtree rules in docs/AGENTS.md
docs/experiments/  Scientific-method experiments (predictions before results)
docs/cookbook/     Step-by-step how-tos
docs/postmortem/   Incident write-ups (not design decisions)
src/               Production code (create when the project has any)
lab/               Throwaway prototypes that are not experiments and not production
ignored/           Local clones, bulky artifacts — never committed. Save scripts that act as macros for the agent's ease of use here. Basically as macros.
Incomplete/        Operator leftovers — never committed
```

## Standing orders

- **Constitution is the long-term track.** Read [docs/constitution.md](docs/constitution.md) at least once in every context window. At project start, create it with the user from that template: save the agent's full vision, refined until the user agrees. Do not leave a TEMPLATE constitution in force, and do not keep the vision only in chat.
- **One home per fact.** Put a rule in the tier that owns it; elsewhere, link. Do not restate.
- **Non-trivial changes get an Agent Note in the same change.** Exempt only mechanical or local edits. Path: `.agents/notes/{lifecycle}/{class}/yyyy-mm-dd-topic.md`.
- **Predictions before results.** Never record experimental outcomes until a `docs/experiments/planned/` file with Hypothesis, Predictions, and Method is written. Do not backfill predictions after seeing data.
- **Experiments are not Agent Notes.** Decisions that change architecture, process, or shipped behavior still get an Agent Note; the run lives under `docs/experiments/`.
- **Incidents are postmortems.** Subtle, systemic, costly-to-rediscover failures go in `docs/postmortem/`, not in Agent Notes or experiment failures.
- **Misconfiguration and failed runs fail loud.** Do not swallow errors, skip missing referents, or leave empty `catch` blocks.
- **Document current state.** Change stories belong in commits, Agent Notes, postmortems, or experiment verdicts — not in durable reference docs.
- **Run `python scripts/verify_template.py`** after adding or moving notes, experiments, or docs. Report the commands you ran.
- **Cross link documentation**, and when a hard won solution is made that makes it into src/ code, reference the related documents as an inline comment.

## Editing these instructions

Keep each rule self-contained and short. `CLAUDE.md` is a symlink to this file; edit `AGENTS.md`. Subtree `AGENTS.md` files hold only rules that do not belong at root.

## Ai-notes rule

If you have been told to keep your notes in ai-notes or a similar place, instead use .agents/ there are instructions in .agents/ on how to craft high quality notes. You should read its AGENTS.md at least once in your context window to help stay on track.