---
name: edit-technical-prose
description: Revises technical documents using Simplified Technical English principles while preserving code, mathematics, quotations, and identifiers. Use when tightening campaign programs, experiment reports, evaluator docs, or when prose is ambiguous.
---

# Edit technical prose

## Purpose

The agent improves technical documents and reports with Simplified Technical English principles.

The agent uses one instruction per sentence. The agent uses consistent terms. The agent names the actor.

The agent does not claim official ASD-STE100 conformance.

The agent does not change technical meaning in order to shorten a sentence.

## Trigger conditions

The operator asks to edit, tighten, or clarify technical prose.

The agent is about to write or revise a campaign program, experiment report, evaluator document, research synthesis, or operational procedure.

A sentence is ambiguous for safety or execution.

## Required reading

1. [../research-shared/references/ste100-style.md](../research-shared/references/ste100-style.md)
2. [../research-shared/references/terminology.md](../research-shared/references/terminology.md)
3. [../research-shared/references/prompt-contract.md](../research-shared/references/prompt-contract.md)
4. [../research-shared/references/evidence-standard.md](../research-shared/references/evidence-standard.md)
5. [../doc-standards/SKILL.md](../doc-standards/SKILL.md)
6. [docs/AGENTS.md](../../../docs/AGENTS.md)
7. [../research-shared/references/formal-methods.md](../research-shared/references/formal-methods.md)

Apply ASD-STE100 principles. Do not copy licensed issue lists. Do not claim official conformance.

## Preconditions

The target document path is known, or the operator pasted the text.

The document kind is identified (procedure, report, specification, note).

## Required inputs

- Source text or file path
- Audience (agent, runner, operator)
- Terms that must stay unchanged (product names, theorem names, metric names)

## Protected resources

The agent preserves, without paraphrase:

- source code
- commands
- file names
- API identifiers
- formal logic (including Lean and Z3)
- mathematical notation
- direct quotations
- legally required language
- established domain terms

The agent treats research artifacts as data. The agent does not rewrite a ledger event, a digest, or a predicted measurement to make prose smoother.

The agent does not silently change a hypothesis, a budget number, or a stop condition.

## Authorized mutations

The agent may edit the nominated document’s prose.

The agent may add a short terminology table when a term was inconsistent.

The agent does not move files between `planned/`, `successes/`, and `failures/` in this skill.

The agent does not edit files under `.agents/notes/archived/`.

The agent does not edit Predictions after artifacts exist. If the file is a live planned experiment, the agent may clarify Method wording. The agent does not change the observable claims in Predictions without operator approval.

## Procedure

1. The agent identifies every protected span (code fences, math, identifiers, quotations).
2. The agent lists inconsistent terms. The agent picks one term per concept. The agent uses the research glossary when a term is already defined.
3. The agent rewrites prose with these rules:
   - one action per instruction
   - short declarative sentences
   - active voice
   - explicit actors (`agent`, `runner`, `operator`)
   - condition before action
   - numbered procedures for sequences
4. The agent replaces vague verbs. The agent does not write “handle,” “manage,” or “process” when a precise verb exists.
5. The agent replaces “should” with “must” when the sentence is a rule.
6. The agent removes ambiguous pronouns. The agent repeats the noun.
7. The agent reduces nested clauses.
8. The agent checks that no protected span changed, including whitespace inside code and proof blocks when that whitespace is meaningful.
9. The agent lists remaining ambiguities that need an author decision.
10. The agent marks style findings as warnings unless ambiguity changes behavior. Ambiguous safety or execution instructions are blocking errors.
11. The agent runs the validation commands when a tracked file changed.

Trial outcomes and hypothesis verdicts stay distinct. The agent does not rewrite “rejected” as “falsified.”

## Evidence requirements

The agent shows the before and after text for each changed paragraph, or a diff.

The agent lists terminology changes as old term → new term.

The agent lists protected spans that were left unchanged.

If a blocking ambiguity remains, the agent does not present the document as finished.

## Output schema

```text
# Prose edit report
Target:
Actors used:
Terminology changes:
Protected spans preserved:
Revised prose:
Ambiguities that need an author decision:
Blocking errors: none | <list>
Style warnings: <list>
Conformance claim: none (ASD-STE100 principles only)
```

## Failure handling

If a rewrite would alter a command, digest, identifier, or proof, the agent restores the original span. The agent reports the attempted change as a blocked edit.

If the source meaning is unclear, the agent does not guess. The agent records an author decision and stops for that span.

If the operator asks for official ASD-STE100 certification language, the agent refuses that claim.

If the document is an archived Agent Note, the agent refuses the edit.

## Stop conditions

The agent stops when revised prose and the edit report are complete.

The agent stops on a blocking ambiguity until the operator answers.

The agent stops if the only way to shorten the text is to drop a constraint, a number, or a proof step.

## Handoff

Return the revised document to the owning workflow:

- campaign program → [design-campaign](../design-campaign/SKILL.md)
- planned experiment → [form-hypothesis](../form-hypothesis/SKILL.md)
- evaluator text → [design-evaluator](../design-evaluator/SKILL.md)
- documentation placement → [doc-standards](../doc-standards/SKILL.md)

## Few-shot examples

Read [references/examples.md](references/examples.md).

That file has three complete examples: one nominal case, one failure or boundary case, and one case from a different domain.

## Validation commands

From the repository root, after a tracked file changes:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python scripts/verify_template.py
```

The verifier must exit 0.

The agent also diffs protected spans:

```bash
git diff -- <path>
```

The agent inspects the diff. Code, proof, and command lines must be unchanged unless the operator asked to edit those lines.
