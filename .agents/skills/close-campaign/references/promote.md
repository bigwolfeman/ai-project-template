# Promote phase

The agent prepares a human-reviewed promotion package. The agent never merges to `src/` without explicit operator approval in this session.

## Preconditions

`reports/synthesis.md` names the candidate. `reports/integrity-audit.md` is `pass` or `pass_with_risks`. Candidate has an immutable identifier. Reproduction inputs exist. Destination under `src/` is named by the operator or explicitly unknown.

Refuse when the operator asks to copy campaign output into `src/` in the same turn with no review, no Agent Note, and no reproduction. Refuse `git reset --hard` to “clean” a tree for promotion.

## Steps

1. The agent confirms synthesis names the candidate and the audit has no blocking findings. Else stop.
2. The agent presents the promotion package outline to the operator. The agent does not write `src/` in this step.
3. The agent creates a clean worktree under `ignored/research/<slug>/worktrees/promotion-<candidate-id>/` at the candidate identifier. The agent does not use `git reset --hard` on the operator’s working tree.
4. The agent runs documented tests from that clean environment with `env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH`. If a proof plan exists, the agent runs the documented solver or prover when present; if absent, records `not executed` and does not claim a proof result.
5. The agent reviews complexity and operations: new dependencies, line growth, runtime requirements, rollback.
6. The agent writes `reports/promotion-<candidate-id>.md`.
7. The agent searches `.agents/notes/` for the same decision. The agent writes a proposed Agent Note (Problem, Proposal, Alternatives considered, Acceptance criteria, Risks) following [maintain-docs](../../maintain-docs/SKILL.md) for placement and supersession.
8. The agent stops for operator review. Human review is required. Silence is not approval. A prior campaign `accepted` trial is not a production merge.
9. If the operator rejects, the agent leaves `src/` unchanged and records rejection in the promotion report. Candidate identifier remains in the ledger.
10. If the operator approves, the agent copies only approved paths into `src/`, updates docs for current behavior, moves the Agent Note to `implemented/`, and rewrites Proposal into Decision.

## Output

```text
# Promotion package
Campaign:
Candidate identifier:
Synthesis report:
Audit report:
Operator review: pending | approved | rejected
src/ writes allowed: no | yes after approval

## Reproduction
Clean environment path:
Commands:
Results:
Proof plan link:           # or none
Proof result:              # including not executed

## Review
Complexity:
Operations:
Rollback:
Documentation to update:

## Decision record
Agent Note path:
Note status: proposed | implemented | rejected

## Production changes
Paths to write after approval:
Paths written:
```

## Refusals

Silent promotion. Auto-merge. Merge without Agent Note. Inventing a `src/` destination. Patching Predictions or the evaluator lock to make reproduction pass. `git reset --hard`. Continuing after a protected digest change during reproduction.
