# Project Constitution

**Status**: TEMPLATE — not yet the law of a real project. Replace every `[bracket]` block with this project's own facts. Delete the template instructions. Set **Status** to `Ratified` when the user agrees the vision is accurate.

**Version**: 0.0.0
**Ratified**: [YYYY-MM-DD or unfilled]
**Last Amended**: [YYYY-MM-DD or unfilled]

This file is the long-term track for the project. It holds the full vision — what we are building, for whom, what success looks like, what we refuse to build, and the principles that keep later work from drifting. Standing orders and file layout live in [AGENTS.md](../AGENTS.md); **why this project exists** lives here.

Fill it with the user. Do not invent a vision and leave it unreviewed. Do not leave brackets in a ratified constitution.

## Vision

[One to three paragraphs. The agent's complete current understanding of the project, refined with the user. What the thing is. What world it assumes. What "done" feels like years out, not just the next patch.]

## Problem

[Whose problem, in concrete terms. What is painful or impossible today.]

## Users and operators

[Who uses it. Who runs it. Who is harmed if it is wrong.]

## Scope

**In scope**

- [Must exist for the vision to be real]

**Out of scope (non-goals)**

- [Tempting adjacent work we are not doing, and why]

## Success criteria

[Observable outcomes, not slogans. How a later agent would know the project is still on the rails.]

## Constraints

[Language, runtime, hardware, licenses, privacy, safety, budget, "must run on this machine", compatibility. Empty if none yet — say so.]

## Principles

Project-specific rules that force good organization. Not a copy of `AGENTS.md`.

### Principle 1: [Name]

**The rule**: [Declarative]

**Why**: [What drift this prevents]

**How to apply**: [Concrete]

### Principle 2: [Name]

**The rule**:

**Why**:

**How to apply**:

[Add principles as the project learns. Remove principles nobody follows.]

## Architecture sketch

[How the major pieces relate. Where production code lives for *this* stack. Integration boundaries. Link Agent Notes for decisions; do not duplicate them.]

## When this constitution applies

- All new work that could change what the project is
- Features, refactors, and promotions into production

**Override**: only with explicit user authorization and a one-line rationale recorded in the change. If the vision itself changed, amend this file with the user; do not silently ignore it.

## Governance

Amend with the user when the vision or a principle is wrong. Bump:

- MAJOR: the project is a different thing
- MINOR: new principle or new in-scope capability
- PATCH: clarification

Record substantial amendments in an Agent Note under `.agents/notes/`.
