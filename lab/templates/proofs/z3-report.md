# Z3 proof report

Copy this file when the proof plan selects Z3. Fill every field. Link the parent proof plan.

Campaign: `smem-tiles`

Parent proof plan: `lab/campaigns/smem-tiles/reports/proof-tile-limits.md`

## Property

For integers `TM`, `TN` in `{8,16,...,128}`, `smem_bytes(TM,TN) <= 228 * 1024`. Among satisfying assignments, maximize `TM * TN`.

## Assumptions

- Per-block shared memory limit is 228 KiB (`228 * 1024` bytes).
- `smem_bytes(TM,TN)` is the operator-stated static formula (example below uses `4 * TM * TN` bytes).
- `TM` and `TN` are positive multiples of 8. Each is at most 128.
- No dynamic shared memory. One block occupancy target.
- The solver result speaks about the encoded formula and the stated bound only.

## Definitions

| Name | Meaning |
|---|---|
| `TM` | Tile height |
| `TN` | Tile width |
| `smem_bytes` | Static shared-memory byte count for one block |
| admissible | Satisfies bounds, multiples, and the shared-memory inequality |

## Scope

Encoded tile configuration space under the shared-memory bound. Not the CUDA compiler, occupancy heuristics, or other GPU SKUs.

## Solver identity

- Tool: Z3
- Version: `<z3 --version output, or "not installed — command documented">`
- Logic: `QF_LIA`

## Model summary

Variables: `TM`, `TN` (integers).

Constraints:

1. `TM` and `TN` are in `{8,16,...,128}`.
2. `smem_bytes = 4 * TM * TN`.
3. `smem_bytes <= 228 * 1024`.
4. Objective: maximize `TM * TN` (encode with soft constraints, optimize, or a documented search script).

Offline sketch (does not require Z3 to exist for template verification):

[examples/tile-limits.smt2](examples/tile-limits.smt2)

## Execution command

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH z3 -smt2 ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2
```

Alternate check for a claimed larger assignment (counterexample search):

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH z3 -smt2 ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits_counterexample.smt2
```

## Result

not executed

When the operator or agent runs the command, replace this field with `sat`, `unsat`, `counterexample`, or `error`. Paste the solver model or unsat core under Evidence. Do not invent a result.

## Optimal or witness assignment

`<TM=?, TN=?, smem_bytes=? — fill only after a real solver run>`

## Model-to-code correspondence

| Model symbol | Production path |
|---|---|
| `TM`, `TN` | Tile macros in `subject/gemm_tiled.cu` |
| `smem_bytes` | Static shared declaration formula used by that kernel |

If no correspondence exists, write: no correspondence — model only.

## Runtime validation

After a satisfying assignment exists, run:

```bash
env -u APPIMAGE -u APPDIR -u LD_LIBRARY_PATH python -m pytest tests/test_tile_launch.py -q
```

Do not skip that test because an SMT script exists.

## Unproved behavior

- Compiler padding and alignment
- Occupancy and register pressure
- Dynamic shared memory
- Other GPU shared-memory capacities
- Full kernel functional correctness

## Forbidden certainty language

Do not write “proved correct” for `subject/gemm_tiled.cu`. State the exact proposition about formula `F` under bound `N` in solver version `V`.

## Evidence

- SMT artifact path: `ignored/research/smem-tiles/artifacts/proofs/tile-limits/tile_limits.smt2`
- Solver log path: `<fill after run>`
- Pointer: `lab/campaigns/smem-tiles/pointers/proof-tile-limits.md`
