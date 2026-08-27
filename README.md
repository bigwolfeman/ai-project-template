# AI project template

A starter for AI-assisted repositories. It enforces the documentation layout used by [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (nested `AGENTS.md`, path-encoded Agent Notes, one home per fact) and adds a scientific-method experiment tree.

This is not a fork of the harness. Product, plugin, and bilingual machinery stay with upstream.

## Use it

```sh
git clone https://github.com/bigwolfeman/ai-project-template.git my-project
cd my-project
python scripts/verify_template.py
```

Then follow [.agents/cookbook/starting-a-project.md](.agents/cookbook/starting-a-project.md).

## What agents must do

| Kind of work | Where it goes |
|---|---|
| Standing orders | [AGENTS.md](AGENTS.md) |
| Project vision (fill at start) | [docs/constitution.md](docs/constitution.md) |
| Design decisions | [.agents/notes/](.agents/notes/README.md) |
| How-tos | [.agents/cookbook/](.agents/cookbook/starting-a-project.md) |
| Experiments | [lab/experiments/](lab/experiments/README.md) — **predictions first** |
| Escaped bugs | [.agents/postmortem/](.agents/postmortem/README.md) |
| Spikes | [lab/spikes/](lab/spikes/README.md) — informal exploration; no prior hypothesis |
| Campaigns | [lab/campaigns/](lab/campaigns/README.md) — bounded programs with trials |
| Production code | `src/` |

`Incomplete/` and `ignored/` are gitignored. Put local clones and bulky artifacts in `ignored/`. Campaign worktrees live under `ignored/research/<slug>/`.

## Verify

```sh
python scripts/verify_template.py
```
