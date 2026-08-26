# Starting a project from this template

1. Clone or use this repository as the GitHub template.
2. With the user, turn [docs/constitution.md](../constitution.md) from a TEMPLATE into a ratified vision: what the project is, who it is for, success, non-goals, constraints, and principles. Do not leave brackets. Agents must reread that file at least once every context window.
3. Edit root [AGENTS.md](../../AGENTS.md) only for standing orders that are not the vision.
4. Keep `.agents/notes/implemented/process/2026-08-20-template-structure-from-harness.md` or archive it once the new project has its own process notes.
5. The agent puts production code in `src/`. The agent puts informal spikes in `lab/spikes/`. The agent puts campaigns in `lab/campaigns/`.
6. Run `python scripts/verify_template.py` in CI if you add CI.
