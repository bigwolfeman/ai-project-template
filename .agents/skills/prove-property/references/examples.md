# Few-shot examples — prove-property

Each example has a domain, a kind, an input, a decision summary, actions, an output, and stop behavior.

The agent does not include private chain-of-thought. The decision summary is the observable reasoning checkpoint.

Live Z3 or Lean binaries are not required. The agent documents commands and artifacts. The agent does not invent solver results.

## Example 1 — Nominal: Z3 tile-size limits

**Domain:** machine learning / GPU kernels

**Kind:** nominal

### Input

Operator, campaign `tok-arch-lm` (or a kernel campaign `smem-tiles`):

> Prove that no allowed tile size can exceed shared-memory limits and find the largest valid tile.

Operator-stated hardware: 228 KiB shared memory per block, tile variables `TM`, `TN` positive multiples of 8, each at most 128. Production kernel: `subject/gemm_tiled.cu`. Tests: `tests/test_tile_launch.py` (mutable test path, not the protected evaluator).

`z3` may be absent.

### Decision summary

- This is a finite constraint and optimization problem. Z3 is the cheapest sound method. Unit tests cannot enumerate the configuration space. Lean is more expensive than needed.
- Encode hardware limits and tile variables. Request a model for the optimum. Request a counterexample for any claimed larger configuration.
- Validate the selected configuration with a runtime test. Do not skip that test because a solver script exists.
- Do not state “proved correct” for the production GPU kernel. The claim is about the encoded formula under the stated shared-memory bound.
- If `z3` is absent, write the SMT artifact and command. Set Result to `not executed`.

### Actions

1. The agent writes the property: no admissible `(TM, TN)` has `bytes(TM, TN) > 228 KiB`; among admissible pairs, maximize `TM * TN`.
2. The agent records assumptions: static shared-memory formula supplied by the operator; no dynamic shared memory; one block occupancy target.
3. The agent writes `ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2` and a pointer under `lab/campaigns/smem-tiles/pointers/`.
4. The agent writes `lab/campaigns/smem-tiles/reports/proof-tile-limits.md`.
5. The agent documents `z3 -smt2 ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2`.
6. The agent links runtime validation `tests/test_tile_launch.py` for the selected assignment.
7. The agent does not mutate protected evaluator paths.

### Output

`lab/campaigns/smem-tiles/reports/proof-tile-limits.md` excerpt:

```text
# Proof plan
Campaign: smem-tiles
Property: For integers TM, TN in {8,16,...,128}, smem_bytes(TM,TN) <= 228 * 1024.
          Maximize TM*TN among satisfying assignments.
Assumptions: operator smem formula; no dynamic smem; bound is per-block 228 KiB.
Definitions: TM, TN, smem_bytes
Scope: encoded tile configuration space; not the full CUDA toolchain
Method selected: Z3, then one runtime test of the chosen assignment
Why this method is cheapest and sound for the claim: finite constraints and
  optimization; tests cannot enumerate the space; Lean is not required
Solver or prover version: not installed — command documented
Execution command: z3 -smt2 ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2
Result: not executed
Model-to-code correspondence: TM,TN map to tile macros in subject/gemm_tiled.cu
Unproved behavior: compiler padding, occupancy, register pressure, other GPUs
Forbidden certainty language used: no
```

SMT-LIB artifact (documented; not executed in this slice):

```smt2
; tile_limits.smt2 — shared-memory bound 228 KiB
(set-logic QF_LIA)
(declare-const TM Int)
(declare-const TN Int)
; ... encode multiples of 8, bounds, smem_bytes, maximize TM*TN ...
; command: z3 -smt2 tile_limits.smt2
```

Runtime validation link: `tests/test_tile_launch.py`.

Explicit hardware assumptions: 228 KiB per-block shared memory; formula as stated by the operator.

### Stop behavior

The agent stops when the plan, SMT artifact, pointer, and runtime-test link exist. The agent does not fail the skill because `z3` is absent. The agent does not write “the kernel is proved correct.” The agent does not start a training loop.

## Example 2 — Failure / boundary: “proved correct” on a simplified float model

**Domain:** machine learning / GPU kernels (same family of request)

**Kind:** failure / boundary

### Input

Operator:

> Z3 showed unsat for overflow in our 3-variable real model of the kernel. Mark gemm_tiled.cu proved correct and skip the unit tests.

The model uses unbounded reals. Production code uses IEEE-754 `float` and shared memory. No model-to-code correspondence file exists. Unit tests already cover launch bounds.

### Decision summary

- Tests remain cheaper and sufficient for launch-bound behavior. The agent does not skip them.
- A Z3 result on a simplified real model is not a proof of the CUDA kernel.
- “Proved correct” is forbidden. The agent refuses that sentence.
- Missing correspondence is a required field. The agent states that no correspondence exists. The agent does not hide it.
- If the operator still wants the real-model check documented, Result must name formula F and bound N, not the production file.

### Actions

1. The agent refuses to write “proved correct.”
2. The agent writes a plan that selects unit tests as the primary method and records the real-model Z3 script as a separate, weaker artifact if the operator still wants it.
3. The agent fills Unproved behavior: floating-point rounding, memory traffic, compiler transforms.
4. The agent does not skip `tests/test_tile_launch.py`.
5. The agent does not mutate `src/`.

### Output

```text
# Proof plan failure
error: forbidden certainty language
refused: "proved correct" for simplified real model of gemm_tiled.cu
method_required: unit tests (cheapest sound for launch bounds)
optional_artifact: real-model SMT with Result naming formula F only
unproved: IEEE-754, shared-memory layout, full kernel
state_transition: none
```

Allowed substitute sentence if the SMT file is kept:

> Z3 reports unsatisfiable for formula F under bound N in solver version V. This does not prove `subject/gemm_tiled.cu` correct.

### Stop behavior

The agent stops without a production-correctness claim. The agent fails loud if the only requested output is the forbidden sentence. The agent does not invent an `unsat` result when the command was not run.

## Example 3 — Different domain: Lean merge preserves sorted order

**Domain:** algorithms

**Kind:** different domain

### Input

Operator:

> Prove that the merge operation preserves sorted order for all valid inputs.

Subject: `subject/merge.py`. Comparator is a total order on keys. The project wants a general theorem, not bounded examples. Runtime tests exist at `tests/test_merge.py`. `lake` may be absent.

### Decision summary

- Use Lean when the project needs a general theorem. Property-based tests are cheaper for many bugs but do not prove all valid inputs.
- Define sortedness and merge precisely. Prove the preservation theorem. State assumptions about the comparator.
- Link the theorem to the production implementation or a verified reference implementation. If the Lean merge is a model, say so.
- Retain runtime tests for integration behavior. Do not skip them because a Lean file exists.
- Do not state “proved correct” for `merge.py` if FFI, mutability, or exceptions are outside the model.

### Actions

1. The agent writes Property: for all lists `xs`, `ys` that are sorted under `le`, `merge xs ys` is sorted under `le`.
2. The agent records Assumptions: `le` is a total order; inputs are finite lists; no concurrent mutation.
3. The agent writes Lean modules under `ignored/research/merge-sorted/artifacts/proofs/merge-preserves/` and a pointer.
4. The agent writes `lab/campaigns/merge-sorted/reports/proof-merge-preserves.md` (or `docs/experiments/algorithms/yyyy-mm-dd-merge-preserves-proof.md` if no campaign).
5. The agent documents `lake build` in that directory.
6. The agent links `tests/test_merge.py` as remaining integration tests.
7. If `lake` is absent, Result is `not executed`.

### Output

```text
# Proof plan
Campaign: merge-sorted
Property: sorted xs → sorted ys → sorted (merge xs ys)
Assumptions: le is a total order; finite lists; no concurrent mutation
Definitions: sorted, merge, le
Scope: Lean lists and the modeled merge; not CPython allocation or exceptions
Method selected: Lean preservation theorem, plus runtime tests
Why this method is cheapest and sound for the claim: general theorem over all
  valid inputs; tests cannot cover all lists
Solver or prover version: not installed — command documented
Execution command: lake build
Result: not executed
Model-to-code correspondence: merge in Lean maps to subject/merge.py lines L1–Ln
  or "no correspondence — model only"
Unproved behavior: exceptions, mutation, comparator side effects, integration
Forbidden certainty language used: no
```

Lean sketch (artifact; command documented):

```lean
-- MergePreserves.lean
-- theorem merge_preserves_sorted
--   (le : α → α → Prop) [LinearOrder α]
--   (xs ys : List α) (hxs : Sorted le xs) (hys : Sorted le ys) :
--   Sorted le (merge le xs ys)
-- command: lake build
```

Remaining integration assumptions: CPython runtime, file I/O if any, comparator purity in production.

### Stop behavior

The agent stops when the Lean artifact, build command, correspondence statement, unproved remainder, and runtime-test link exist. The agent does not require `lake` to be installed. The agent does not promote `merge.py` into `src/`. The agent does not start an unbounded search for a nicer proof.
