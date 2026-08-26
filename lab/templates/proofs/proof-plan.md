# Proof plan

Copy this file into `lab/campaigns/<slug>/reports/proof-<property-slug>.md` (or into `docs/experiments/algorithms/yyyy-mm-dd-<property-slug>-proof.md` when there is no campaign). Replace every field. Do not leave template guidance in a live report.

Campaign: `<slug or "none — standalone">`

Property:

`<exact proposition>`

Assumptions:

- `<what the argument takes as given>`

Definitions:

- `<name>` — `<meaning>`

Scope:

`<system, bound, or fragment>`

Method selected:

`<unit tests | property-based tests | differential tests | Z3 | Lean | combination>`

Why this method is cheapest and sound for the claim:

`<one short paragraph>`

Solver or prover version:

`<version string, or "not installed — command documented">`

Execution command:

```bash
<reproducible command>
```

Result:

`<sat | unsat | proved | counterexample | error | not executed>`

Model-to-code correspondence:

`<paths and mapping, or "no correspondence — model only">`

Unproved behavior:

- `<what remains outside the claim>`

Forbidden certainty language used: no

Artifact paths:

- `<relative path to model or script>`

Pointer paths:

- `<relative path under pointers/, if any>`

Runtime tests that remain:

- `<relative path to tests>`

## Field guidance

| Field | Rule |
|---|---|
| Property | Exact proposition. Do not paraphrase into a slogan. |
| Assumptions | Bound, hardware, comparator, and language assumptions. Do not invent them. |
| Scope | Name the model fragment. Do not claim the full production system unless the model covers it. |
| Method selected | Cheapest sound method. See [formal-methods.md](../../../.agents/skills/research-shared/references/formal-methods.md). |
| Result | Record the actual solver or prover outcome. If the tool is absent, use `not executed`. Do not invent `unsat`, `sat`, or `proved`. |
| Unproved behavior | Always list remainder. Never hide missing correspondence. |

## Filled example (Z3 tile limits)

Campaign: `smem-tiles`

Property:

For integers `TM`, `TN` in `{8,16,...,128}`, `smem_bytes(TM,TN) <= 228 * 1024`. Maximize `TM * TN` among satisfying assignments.

Assumptions:

- Operator shared-memory formula is static.
- No dynamic shared memory.
- Bound is 228 KiB per block.

Definitions:

- `TM`, `TN` — tile dimensions
- `smem_bytes` — operator-supplied byte formula

Scope:

Encoded tile configuration space. Not the full CUDA toolchain.

Method selected:

Z3, then one runtime test of the chosen assignment.

Why this method is cheapest and sound for the claim:

Finite constraints and optimization. Unit tests cannot enumerate the space. Lean is not required.

Solver or prover version:

not installed — command documented

Execution command:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH z3 -smt2 ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2
```

Result:

not executed

Model-to-code correspondence:

`TM`, `TN` map to tile macros in `subject/gemm_tiled.cu`.

Unproved behavior:

- Compiler padding
- Occupancy
- Register pressure
- Other GPU SKUs

Forbidden certainty language used: no

Artifact paths:

- `ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2`

Pointer paths:

- `lab/campaigns/smem-tiles/pointers/proof-tile-limits.md`

Runtime tests that remain:

- `tests/test_tile_launch.py`
