# Simplified Technical English principles

Apply ASD-STE100 principles to research prose. Do not copy licensed issue lists. Do not claim official ASD-STE100 conformance. This project has no authorized conformance process.

Names: write “ASD-STE100” or “Simplified Technical English.” Do not write “AD-STE100.”

This file owns the style rules and the edit checklist. The former standalone `edit-technical-prose` skill is demoted here; do not invent a second home for these steps.

## Scope

The agent applies this style to:

- Agent instructions
- Campaign programs
- Experiment reports
- Evaluator documentation
- Research syntheses
- Operational procedures
- Error messages

## Core rules

The writer must:

1. Put one action in each instruction.
2. Use short declarative sentences.
3. Use active voice.
4. Name the actor: the operator, the agent, the runner, the evaluator, the comparator, or the verifier.
5. Use the terms in [terminology.md](terminology.md). Do not invent synonyms.
6. Define an abbreviation at first use.
7. Use a concrete verb.
8. Use a positive instruction when that instruction is safe.
9. Number a procedure.
10. State the condition before the action.

The writer must not:

- Use an ambiguous pronoun when several nouns are possible
- Stack long noun clusters
- Switch terms for the same object
- Hide an exception in a later paragraph
- Use vague modifiers such as “appropriate,” “robust,” or “properly”
- Use metaphorical process language
- Write “handle,” “manage,” or “process” when a precise verb exists
- Write “should” when the rule means “must”
- Use motivational language in place of an instruction
- Use an unbounded directive such as “never stop”

## Exceptions

The editor must preserve:

- Source code
- Commands
- File names
- API identifiers
- Formal logic
- Mathematical notation
- Direct quotations
- Legally required language
- Established domain terms

The editor must not damage technical meaning to shorten a sentence.

Identifiers stay in backticks. Mathematics stays in the author’s notation. A skill name such as `run-campaign` is an identifier. Do not rewrite it into a “simpler” name.

## Review checklist

The reviewer asks:

1. Does each sentence name the actor?
2. Does each instruction contain one action?
3. Do trial outcomes and hypothesis verdicts stay distinct?
4. Do code, mathematics, and identifiers remain unchanged?
5. Does the text claim official ASD-STE100 conformance? If yes, the reviewer removes that claim.
6. Would a later agent execute the wrong action because a pronoun or condition is ambiguous?

Style findings are warnings unless ambiguity changes behavior. Ambiguous safety or execution instructions are blocking errors.

## Examples of principle, not of a licensed list

Acceptable: “The agent writes predictions. The agent commits the planned file. The agent then runs the protocol.”

Unacceptable: “After handling things, we should probably process the results and never stop improving.”

Acceptable: “Z3 reports unsatisfiable for formula F under bound N.”

Unacceptable: “We proved the system correct.”

## Edit checklist

Use this checklist when the operator asks to edit, tighten, or clarify technical prose, or when the agent is about to revise a campaign program, experiment report, evaluator document, research synthesis, or operational procedure.

### Preserve without paraphrase

- Source code and commands
- File names and API identifiers
- Formal logic (including Lean and Z3) and mathematical notation
- Direct quotations and legally required language
- Established domain terms and research glossary terms
- Ledger events, digests, and predicted measurements (do not smooth them)
- Hypothesis text, budget numbers, and stop conditions (do not change silently)

Do not edit files under `.agents/notes/archived/`. Do not move experiment files between `planned/`, `successes/`, and `failures/` while editing prose. For a live planned experiment, the agent may clarify Method wording. The agent does not change observable claims in Predictions without operator approval. Trial outcomes and hypothesis verdicts stay distinct (do not rewrite “rejected” as “falsified”).

### Revise prose

1. Identify every protected span (code fences, math, identifiers, quotations).
2. List inconsistent terms. Pick one term per concept. Use [terminology.md](terminology.md) when a term is already defined.
3. Rewrite with: one action per instruction; short declarative sentences; active voice; explicit actors; condition before action; numbered procedures.
4. Replace vague verbs. Do not write “handle,” “manage,” or “process” when a precise verb exists.
5. Replace “should” with “must” when the sentence is a rule.
6. Remove ambiguous pronouns. Repeat the noun.
7. Reduce nested clauses.
8. Confirm no protected span changed (including meaningful whitespace in code and proof blocks).
9. List remaining ambiguities that need an author decision.
10. Mark style findings as warnings unless ambiguity changes behavior. Ambiguous safety or execution instructions are blocking errors.

### Report term changes

Produce a short edit report:

```text
# Prose edit report
Target:
Actors used:
Terminology changes:   # old term → new term
Protected spans preserved:
Revised prose:         # or point at the diff
Ambiguities that need an author decision:
Blocking errors: none | <list>
Style warnings: <list>
Conformance claim: none (ASD-STE100 principles only)
```

Show before/after text for each changed paragraph, or a diff. If a rewrite would alter a command, digest, identifier, or proof, restore the original span and report a blocked edit. If the source meaning is unclear, do not guess. Refuse official ASD-STE100 certification language.

After a tracked file changes:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
git diff -- <path>
```

The verifier must exit 0. Code, proof, and command lines must be unchanged unless the operator asked to edit those lines.
