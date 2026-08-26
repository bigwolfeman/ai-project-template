# Few-shot examples — edit-technical-prose

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

The agent applies ASD-STE100 principles. The agent does not claim official ASD-STE100 conformance.

## Example 1 — Nominal: bloated campaign paragraph

**Domain:** algorithms / systems (API cache program.md)

**Kind:** nominal

### Input

Operator asks to tighten this paragraph in `lab/campaigns/api-cache/program.md`:

> We should handle the caching situation by processing requests in a way that basically makes things faster and then we just sort of see if it feels snappier for users, and you might want to try a few ideas and never really stop until it seems okay, resetting git if a try is worse so we can keep moving.

Protected spans: none in this paragraph. Budget numbers live in `campaign.yaml` and must not be invented here.

Actors in this repository: agent, runner, operator.

### Decision summary

- The paragraph is a procedure. It needs numbered instructions, explicit actors, and finite stop conditions.
- “NEVER STOP” language is not valid. Replace with declared budgets (refer to `campaign.yaml`, do not invent numbers).
- Destructive Git reset is not allowed. Say that rejected candidates keep identifiers.
- Replace “handle / process / sort of / basically / seems okay.”
- “Should” in a rule becomes “must” only where the campaign contract already requires the action. Do not add new obligations.
- Trial vs hypothesis vocabulary: this paragraph is operational, not a verdict.

### Actions

1. The agent lists vague verbs and unbounded instructions.
2. The agent rewrites with named actors and one action per sentence.
3. The agent does not add a latency number that was not in the source or in `campaign.yaml`.
4. The agent produces the prose edit report.

### Output

Revised prose:

```markdown
The agent compares cache candidates under the campaign evaluator.

The runner records each candidate identifier.

The operator owns the budget and the stop conditions in `campaign.yaml`.

The agent does not follow unbounded loop instructions.

The agent does not use a destructive Git reset to reject a candidate.

The comparator uses the declared latency and memory measurements.
Subjective “snappiness” is not an evaluator metric.
```

Prose edit report (abridged):

```text
# Prose edit report
Target: lab/campaigns/api-cache/program.md (one paragraph)
Actors used: agent, runner, operator
Terminology changes:
- "handle/process" → named verbs (compare, record)
- unbounded continuation → stop conditions in campaign.yaml
- git reset → forbidden destructive reset; keep identifiers
Protected spans preserved: none in the source paragraph
Ambiguities that need an author decision:
- which latency percentile is the objective (not stated in the paragraph)
Blocking errors: none after rewrite (unbounded loop removed)
Style warnings: operator must confirm the percentile lives in campaign.yaml
Conformance claim: none (ASD-STE100 principles only)
```

### Stop behavior

The agent stops after the rewrite and report. The agent does not start trials. If the percentile is still missing from `campaign.yaml`, that is an author decision, not a silent default.

## Example 2 — Failure / boundary: preserve Lean and Z3

**Domain:** formal methods (Lean theorem, Z3 query) inside an otherwise wordy report

**Kind:** failure / boundary (meaning preservation)

### Input

Operator:

> Shorten this. STE100 it. The proof block looks verbose.

Source (outer fences are tildes so inner code fences stay intact):

~~~~markdown
We should probably go ahead and manage the proof so that it shows the
merge thing is fine for all the lists people might pass in.

```lean
theorem merge_sorted
    (xs ys : List α) [LinearOrder α]
    (hxs : Sorted (· ≤ ·) xs) (hys : Sorted (· ≤ ·) ys) :
    Sorted (· ≤ ·) (merge xs ys) := by
  sorry
```

Also this solver bit is noisy but keep the command:

```text
z3 -smt2 tile_limits.smt2
```

```smt2
(assert (<= (* TILE_M TILE_N 4) SHARED_MEM_BYTES))
```
~~~~

The `sorry` and the SMT assertion are the current artifacts. The operator did not ask to complete the proof.

### Decision summary

- Prose around the blocks may be rewritten.
- The Lean theorem, the `sorry`, the `z3` command, and the SMT assertion are protected spans. Do not “shorten” them. Do not replace `sorry` with a proof. Do not pretty-print SMT into different logic.
- File names `tile_limits.smt2` stay unchanged.
- Do not claim the merge operation is proved. `sorry` means the theorem is not proved.
- Blocking: a rewrite that implied a completed proof would be a false claim.

### Actions

1. The agent marks the Lean fence, the z3 command, and the SMT line as protected.
2. The agent rewrites only the surrounding prose with explicit actors.
3. The agent leaves the fences byte-for-byte unchanged.
4. The agent reports that completing `sorry` is out of scope for this skill.

### Output

Revised prose (protected spans unchanged):

~~~~markdown
The agent states the merge-sortedness claim in Lean.

The theorem is not proved. The proof body is `sorry`.

```lean
theorem merge_sorted
    (xs ys : List α) [LinearOrder α]
    (hxs : Sorted (· ≤ ·) xs) (hys : Sorted (· ≤ ·) ys) :
    Sorted (· ≤ ·) (merge xs ys) := by
  sorry
```

The operator runs the solver with this command:

```text
z3 -smt2 tile_limits.smt2
```

```smt2
(assert (<= (* TILE_M TILE_N 4) SHARED_MEM_BYTES))
```

The agent does not claim production merge is verified. Runtime tests remain required for integration.
~~~~

Prose edit report (abridged):

```text
Protected spans preserved:
- Lean theorem merge_sorted (including sorry)
- command z3 -smt2 tile_limits.smt2
- SMT assertion on TILE_M TILE_N SHARED_MEM_BYTES
Terminology changes: "manage the proof" → "states the claim"; no conformance claim
Blocking errors: none (proof status still unproved)
Ambiguities that need an author decision: none for the protected spans
Conformance claim: none (ASD-STE100 principles only)
```

### Stop behavior

The agent stops. The agent does not fill `sorry`. The agent does not retune Z3 flags. If the operator insists on deleting the Lean block because it is “verbose,” the agent refuses that deletion as a blocked edit.

## Example 3 — Different domain: bug investigation notes

**Domain:** bug investigation (deadlock report)

**Kind:** different domain

### Input

Operator asks to clarify this issue blurb before it is copied into a campaign report:

> It didn’t deadlock that time so I guess we fixed it. Someone should handle the worker thing. The trace `artifacts/deadlock-2026-08-20.zst` probably still matters but maybe not. We processed the stress test and it was fine once.

Protected: filename `artifacts/deadlock-2026-08-20.zst`. Trial vocabulary must stay distinct from hypothesis verdicts.

### Decision summary

- “Did not deadlock that time” is inconclusive, not a fix, not `supported`.
- Ambiguous pronouns (“it,” “someone”) must become nouns and actors.
- The trace filename is protected.
- “Fine once” is not acceptance under a stress protocol.
- Blocking: the original last sentence would authorize promotion. That execution meaning is wrong. The rewrite must not keep that authorization.

### Actions

1. The agent marks `artifacts/deadlock-2026-08-20.zst` as protected.
2. The agent rewrites with operator/agent/runner actors.
3. The agent uses trial outcome `inconclusive` for a single non-reproduction.
4. The agent lists the remaining author decision: what stress count constitutes acceptance (must come from the campaign, not this editor).

### Output

Revised prose:

```markdown
One run did not deadlock. That trial outcome is inconclusive. It is not a fix.

The operator keeps the failing trace at `artifacts/deadlock-2026-08-20.zst`.

The agent does not treat a single passing stress run as acceptance.

The runner records stress and regression results against the evaluator contract.

The operator decides promotion after those results meet the campaign rule.
```

Prose edit report (abridged):

```text
Target: deadlock issue blurb
Actors used: agent, runner, operator
Terminology changes:
- "fixed it" → not a hypothesis verdict; single non-repro is inconclusive
- "handle the worker thing" → removed; no precise action was stated
Protected spans preserved: artifacts/deadlock-2026-08-20.zst
Ambiguities that need an author decision:
- required stress-run count (campaign.yaml / evaluator spec)
Blocking errors: original text implied the bug was fixed; rewrite removes that claim
Style warnings: none remaining in the revised paragraph
Conformance claim: none (ASD-STE100 principles only)
```

### Stop behavior

The agent stops until the operator supplies the stress-count rule if the report needs a numeric acceptance line. The agent does not invent that number. The agent does not mark a hypothesis `supported`.
