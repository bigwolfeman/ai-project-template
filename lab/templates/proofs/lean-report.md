# Lean proof report

Copy this file when the proof plan selects Lean. Fill every field. Link the parent proof plan.

Campaign: `merge-sorted`

Parent proof plan: `lab/campaigns/merge-sorted/reports/proof-merge-preserves.md`

## Property

For all finite lists `xs` and `ys`, if `xs` is sorted under `le` and `ys` is sorted under `le`, then `merge le xs ys` is sorted under `le`.

## Assumptions

- `le` is a total order (linear order) on the element type.
- Inputs are finite lists.
- No concurrent mutation of list structure during merge.
- The Lean `merge` is the modeled function named in Definitions.

## Definitions

| Name | Meaning |
|---|---|
| `Sorted le xs` | List `xs` is nondecreasing under `le` |
| `merge le xs ys` | Merge of two lists under comparator `le` |
| `le` | Comparator relation |

## Scope

Lean lists and the modeled merge. Not CPython allocation, exceptions, or mutable Python lists.

## Prover identity

- Tool: Lean 4 via Lake
- Version: `<lake --version / lean --version, or "not installed — command documented">`

## Theorem statement

```lean
theorem merge_preserves_sorted
    {α : Type} (le : α → α → Prop) [LinearOrder α]
    (xs ys : List α)
    (hxs : Sorted le xs) (hys : Sorted le ys) :
    Sorted le (merge le xs ys)
```

Offline sketch (does not require Lake to exist for template verification):

[examples/MergePreserves.lean](examples/MergePreserves.lean)

## Execution command

From the proof package directory (after copy into campaign artifacts):

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH lake build
```

Check Lean alone on a single file when the package layout allows it:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH lean MergePreserves.lean
```

## Result

not executed

When the operator or agent runs the command, replace this field with `proved`, `error`, or `counterexample` as applicable. Paste build output under Evidence. Do not invent `proved`.

## Model-to-code correspondence

| Model symbol | Production path |
|---|---|
| `merge` | `subject/merge.py` lines that implement merge, or “no correspondence — model only” |
| `le` | Comparator passed into that merge |

If the Lean merge is only a model, state that fact. Do not hide it.

## Runtime validation

Retain integration tests:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python -m pytest tests/test_merge.py -q
```

Do not skip those tests because a Lean file exists.

## Unproved behavior

- CPython exceptions and allocation failure
- In-place mutation of Python lists
- Comparator side effects
- FFI or other language boundaries
- Full process integration outside the unit tests

## Forbidden certainty language

Do not write “proved correct” for `subject/merge.py` when FFI, mutability, or exceptions lie outside the model. State the exact theorem above.

## Evidence

- Lean module path: `ignored/research/merge-sorted/artifacts/proofs/merge-preserves/MergePreserves.lean`
- Build log path: `<fill after run>`
- Pointer: `lab/campaigns/merge-sorted/pointers/proof-merge-preserves.md`
