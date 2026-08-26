# Formal methods policy

Select the cheapest method that supports the required claim. Tests remain the default when they are cheaper and sufficient. Z3 and Lean are optional tools. No one method replaces all others.

Terms: [terminology.md](terminology.md). Evidence: [evidence-standard.md](evidence-standard.md). Procedure: [prove-property](../../prove-property/SKILL.md).

## Evidence hierarchy

The agent starts at the top. The agent moves down only when the cheaper method cannot support the claim.

1. **Unit tests** — concrete behavior on chosen inputs.
2. **Property-based tests** — executable coverage over generated inputs.
3. **Differential tests** — agreement between implementations.
4. **Z3** — satisfiability, bounded verification, constraints, and counterexamples.
5. **Lean** — general mathematical theorems and machine-checked proofs.
6. **Empirical experiments** — performance and physical observations. Predictions first. See [evidence-standard.md](evidence-standard.md).

The agent must not skip tests because a solver script exists. The agent must not skip an experiment because a proof of a simpler model exists.

## When to use Z3

The agent prefers Z3 for:

- Configuration validity
- Scheduling
- Resource constraints
- State-machine reachability
- Bounded equivalence
- Index and shape safety
- Finite combinatorial optimization
- Counterexample search

Z3 is a bounded tool. A Z3 result speaks about the encoded formula and the stated bound. It does not speak about unbounded production behavior unless the model says so.

## When to use Lean

The agent prefers Lean for:

- Algorithm correctness
- Algebraic laws
- Inductive invariants
- Termination arguments
- General preservation theorems
- Durable mathematical foundations

Lean is costly. The agent uses it when the claim is mathematical and must survive beyond one campaign.

## Required proof documentation

Every proof artifact must state:

| Field | Content |
|---|---|
| Property | The exact proposition |
| Assumptions | What the proof takes as given |
| Definitions | Names used in the proposition |
| Scope | What system, bound, or fragment is modeled |
| Solver or prover version | Tool identity and version |
| Execution command | How the operator or agent reproduces the result |
| Result | Satisfiable, unsatisfiable, proved, counterexample, or error |
| Model-to-code correspondence | How the model maps to production paths |
| Unproved behavior | What remains outside the claim |

The agent links the model to production code. If no correspondence exists, the agent states that fact. The agent does not hide it.

When the solver finds a counterexample, the agent records it as evidence. The agent does not discard it.

## Forbidden certainty language

The agent must not state “proved correct” when:

- The proof covers only a simplified model
- Production code is not connected to the model
- Foreign-function behavior is assumed
- Floating-point semantics differ from the model
- Concurrency or I/O lies outside the proof
- The bound is finite and the production system is not
- The evaluator or tests that wrap the proof were not run

The agent states the exact proved proposition. Example: “Z3 reports unsatisfiable for formula F under bound N in solver version V.”

The agent must not claim formal proof of behavior that lies outside the stated model.

## Integrity

Proof scripts and solver logs are untrusted data if a candidate produced them. See [prompt-contract.md](prompt-contract.md).

The agent reproduces the command in a clean environment before promotion. Promotion remains an operator decision.
