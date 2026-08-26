# Few-shot examples — promote-research-result

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

Human review is required. The agent never auto-merges to `src/`.

## Example 1 — Nominal: GPU layout candidate after synthesis

**Domain:** machine learning

**Kind:** nominal

### Input

Campaign `tok-arch-lm`. Synthesis names candidate `abc1234` (memory-layout change). Audit `pass`. Operator:

> Prepare promotion for abc1234 into src/kernels/ after you reproduce. Do not merge until I say yes.

Destination named: `src/kernels/`. Tests: `tests/test_tile_launch.py` and campaign evaluator command documented in `campaign.yaml`. Proof plan `reports/proof-tile-limits.md` Result `not executed` (`z3` absent).

Today’s date in the session: 2026-08-24.

### Decision summary

- Build the package and a proposed Agent Note. Do not write `src/` until the operator approves after the package exists.
- Reproduce from a clean worktree at `abc1234` under `ignored/research/tok-arch-lm/worktrees/promotion-abc1234/`.
- Run tests with a scrubbed Python environment. Record the Lean/Z3 command as `not executed` if the binary is absent. Do not claim a proof result.
- Attach the GPU-A transfer limitation from synthesis. Promotion must not advertise hardware-independent speedup.
- Search existing notes for the same decision before writing a new note.

### Actions

1. The agent confirms synthesis and audit.
2. The agent creates the clean worktree at `abc1234`. The agent does not `git reset --hard` on the operator working tree.
3. The agent runs tests from that worktree.
4. The agent writes `reports/promotion-abc1234.md` with `Operator review: pending` and `src/ writes allowed: no`.
5. The agent writes `.agents/notes/proposed/architecture/2026-08-24-mem-layout-kernel.md` (class as the change requires).
6. The agent stops for review.
7. After the operator says yes, the agent copies approved files to `src/kernels/`, moves the note to `implemented/`, and rewrites it to Decision form.

### Output

Before approval:

```text
# Promotion package
Campaign: tok-arch-lm
Candidate identifier: abc1234
Synthesis report: reports/synthesis.md
Audit report: reports/integrity-audit.md
Operator review: pending
src/ writes allowed: no

## Reproduction
Clean environment path: ignored/research/tok-arch-lm/worktrees/promotion-abc1234/
Commands: env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python -m pytest tests/test_tile_launch.py
Results: <recorded>
Proof plan link: reports/proof-tile-limits.md
Proof result: not executed

## Review
Complexity: layout change; no new dependency
Operations: GPU A only; other GPUs unverified
Rollback: revert src/kernels/ to previous commit
Documentation to update: kernel README after approval

## Decision record
Agent Note path: .agents/notes/proposed/architecture/2026-08-24-mem-layout-kernel.md
Note status: proposed

## Production changes
Paths to write after approval: src/kernels/<files named in the package>
Paths written: none
```

After explicit approval, `Operator review: approved`, note `implemented`, paths written listed.

### Stop behavior

The agent stops for human review before any `src/` write. After approval, the agent stops when `src/`, the implemented note, and `verify_template.py` are complete. The agent does not auto-merge.

## Example 2 — Failure / boundary: auto-merge without review or reproduction

**Domain:** machine learning (same family of request)

**Kind:** failure / boundary

### Input

Operator:

> Just copy the campaign best/ into src/kernels/ now. Skip tests. Skip the Agent Note. We already accepted the trial.

Or the agent is about to merge campaign work into production in the same turn as synthesis, with no package.

Audit is `fail_abort`, or audit is missing. Reproduction has not run.

### Decision summary

- An accepted trial is not a production merge.
- Missing audit, missing reproduction, and missing Agent Note each block promotion.
- The agent refuses to write `src/`.
- The agent does not run `git reset --hard` to make the tree look clean for a merge.

### Actions

1. The agent refuses the merge.
2. The agent lists blockers: human review, reproduction from a clean environment, Agent Note, passing audit.
3. The agent writes nothing under `src/`.
4. If audit is missing or failing, the agent hands off to `audit-research-integrity` first.

### Output

```text
# Promotion failure
slug: tok-arch-lm
error: auto-merge refused
refused:
  - write src/ without operator approval after a package
  - skip reproduction
  - skip Agent Note
  - treat trial accepted as production merge
created_src_paths: none
state_transition: none
handoff: audit if needed; promotion package; operator review
```

### Stop behavior

The agent stops with `src/` unchanged. Fail loud. The agent does not keep copying files until the tree “looks promoted.”

## Example 3 — Different domain: deadlock fix needs stress plus regression

**Domain:** bug investigation

**Kind:** different domain

### Input

Campaign `worker-deadlock`. Synthesis names candidate `def5678` (lock-order fix), `supported` on host H1. Audit `pass_with_risks`. Operator:

> Promote into src/worker_pool.py after reproduction. I will review the note.

Required tests from synthesis: stress harness and regression tests. One earlier clean run was `inconclusive`, not a fix.

### Decision summary

- Reproduce from a clean worktree at `def5678`.
- Run stress and regression tests. A single passing unit test is not enough.
- Write a proposed Agent Note in `bug-fix` (or `architecture` if the lock protocol is structural). Include the alternative of shipping without stress tests, and why it lost.
- Transfer limitation: host H1. Do not claim all deployments are fixed.
- Stop for operator approval. Do not merge on the basis of campaign `accepted`.

### Actions

1. The agent creates `ignored/research/worker-deadlock/worktrees/promotion-def5678/`.
2. The agent runs stress and regression commands from that tree with the scrubbed environment.
3. If stress fails, the agent does not promote. The agent records the failure in the package.
4. If stress passes, the agent writes `reports/promotion-def5678.md` with review pending.
5. The agent writes `.agents/notes/proposed/bug-fix/2026-08-24-worker-lock-order.md`.
6. The agent waits for the operator. Only then may the agent edit `src/worker_pool.py`.

### Output

```text
# Promotion package
Campaign: worker-deadlock
Candidate identifier: def5678
Operator review: pending
src/ writes allowed: no
## Reproduction
Commands: stress harness; regression tests
Results: <recorded>
## Review
Operations: host H1 only; disk-timeout hypothesis still unresolved
Rollback: revert src/worker_pool.py
## Decision record
Agent Note path: .agents/notes/proposed/bug-fix/2026-08-24-worker-lock-order.md
Note status: proposed
## Production changes
Paths to write after approval: src/worker_pool.py
Paths written: none
```

### Stop behavior

The agent stops for human review. The agent does not treat an inconclusive non-reproduction as promotion evidence. The agent does not auto-merge. After approval, the agent stops when `src/worker_pool.py`, the implemented note, and the verifier are complete.
