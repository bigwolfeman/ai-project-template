# Simplified Technical English principles

Apply ASD-STE100 principles to research prose. Do not copy licensed issue lists. Do not claim official ASD-STE100 conformance. This project has no authorized conformance process.

Names: write “ASD-STE100” or “Simplified Technical English.” Do not write “AD-STE100.”

The workflow skill is [edit-technical-prose](../../edit-technical-prose/SKILL.md). This file owns the style rules. That skill owns the editing procedure.

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

Identifiers stay in backticks. Mathematics stays in the author’s notation. A skill name such as `manage-research-issues` is an identifier. Do not rewrite it into a “simpler” name.

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
