# AI project template

This is a template for software projects and automated research, built for work done with AI agents. Copy it, fill in the constitution, and start.

It does two things that agents do not do on their own.

First, it makes the agent write down a change as an idea, predict what the change will do, and test the prediction before the change enters the project. The agent does not get to decide afterward what it meant to measure.

Second, it keeps a record of every proposed change, including the ones that failed. The record lives in the repository, in plain files, where you can read it, grep it, review it in a diff, and mine it later for ideas that deserved a second chance.

## Why predictions come first

An agent that sees a result will explain it. Given a small gain it will call the idea confirmed. Given a missed target it will call the idea dead. Both errors are cheap to make and expensive to live with, because a decent idea that is filed as dead is never tried again.

So the order is fixed.

1. Write the hypothesis.
2. Write the predictions: the measured scalar, the bar that counts as a strong result, and the bar that counts as a dead end.
3. Commit the file. Then run the experiment.
4. Compare the measurement to the bars you wrote, and file the result in one of three places.

| Folder | Meaning |
|---|---|
| `lab/experiments/successes/` | The strong bar was cleared. |
| `lab/experiments/mixed/` | There is signal, but it is not a clean win. Some predictions held, or the effect is real and small. The idea stays open. |
| `lab/experiments/refuted/` | A solid dead end. The test was sound, the effect was absent or reversed, and no rescue is left to try. |

When the agent cannot tell `mixed` from `refuted`, it files `mixed` and says why. A crash is not a dead end. A missed strong bar is not a dead end.

Nothing reaches `src/` until a person reviews it.

## Documentation lives with the code

This template follows the literate programming idea that explanation belongs next to the thing it explains. Pseudocode comes before code, and it stays in the code after promotion, as docstrings with links back to the experiment that justified them.

One kind of record cannot sit next to the code: the Agent Note. A note holds a decision, the alternatives that were weighed, and the reasons for the choice. That is too long and too raw to put in a source file. So notes get their own tree, `.agents/notes/`, committed with the code. A database of chat logs would hold the same facts, but you could not diff it, review it, or branch it with the code. Files in the repository can be.

## How the repository is arranged

There are many small instruction files. This is deliberate.

Each directory that needs rules has its own `AGENTS.md`. The agent does not read all of them at once. It reads the root file, then opens the file for the directory it is about to work in. Each file is short, so reading one costs little, and the agent reads it again whenever it returns. The rules show up where they apply and stay out of the way elsewhere.

```
AGENTS.md              Standing orders. Read first.
docs/constitution.md   The project vision. Fill it in with the agent at the start.
.agents/notes/         Decision records, by lifecycle and class.
.agents/skills/        Procedures the agent follows.
.agents/cookbook/      Step-by-step how-tos.
.agents/postmortem/    Failures that escaped, written up.
lab/spikes/            Informal exploration. No hypothesis yet.
lab/experiments/       One hypothesis each. Predictions before results.
lab/campaigns/         Bounded research programs with many trials.
src/                   Production code. Only reviewed work goes here.
ignored/               Local clones and bulky artifacts. Not committed.
```

The three kinds of lab work are different things. A spike is a look around. An experiment tests one claim. A campaign runs many trials against an evaluator that the agent cannot modify, under a fixed budget and a stop condition. The agent names which one it is doing before it starts.

## Using it

```sh
git clone https://github.com/bigwolfeman/ai-project-template.git my-project
cd my-project
rm -rf .git && git init
python scripts/verify_template.py
```

Then read [.agents/cookbook/starting-a-project.md](.agents/cookbook/starting-a-project.md). The first job is the constitution. Until it is filled in and ratified, the agent has no vision to check its work against.

`scripts/verify_template.py` checks that notes, experiments, and algorithm writeups have the structure the rules require. Run it after you add or move any of them.

## Where things go

| Kind of work | Where it goes |
|---|---|
| Standing orders | [AGENTS.md](AGENTS.md) |
| Project vision | [docs/constitution.md](docs/constitution.md) |
| Design decisions | [.agents/notes/](.agents/notes/AGENTS.md) |
| How-tos | [.agents/cookbook/](.agents/cookbook/AGENTS.md) |
| Experiments | [lab/experiments/](lab/experiments/README.md) |
| Spikes | [lab/spikes/](lab/spikes/README.md) |
| Campaigns | [lab/campaigns/](lab/campaigns/README.md) |
| Escaped bugs | [.agents/postmortem/](.agents/postmortem/AGENTS.md) |
| Agent glossary | [.agents/AGENTS.md](.agents/AGENTS.md) |
| Production code | `src/` |

The layout descends from the one used by [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness): nested `AGENTS.md` files, path-encoded notes, one home per fact. This is not a fork of it.
