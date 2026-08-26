"""Compare evaluator results: hard constraints first, then objectives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import ComparatorError

COMPARATOR_OUTCOMES = (
    "dominates",
    "equivalent",
    "regresses",
    "mixed",
    "invalid",
    "inconclusive",
)

TRIAL_FROM_COMPARATOR = {
    "dominates": "accepted",
    "equivalent": "rejected",
    "regresses": "rejected",
    "mixed": "inconclusive",
    "invalid": "invalid",
    "inconclusive": "inconclusive",
}


@dataclass(frozen=True)
class ComparisonResult:
    comparator_outcome: str
    trial_outcome: str
    detail: str
    advance_best: bool


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _constraint_passed(op: str, actual: Any, expected: Any) -> bool:
    if op == "eq":
        return actual == expected
    if op == "neq":
        return actual != expected
    left = _as_number(actual)
    right = _as_number(expected)
    if left is None or right is None:
        return False
    if op == "lt":
        return left < right
    if op == "lte":
        return left <= right
    if op == "gt":
        return left > right
    if op == "gte":
        return left >= right
    if op == "in_range":
        if not isinstance(expected, (list, tuple)) or len(expected) != 2:
            return False
        lo = _as_number(expected[0])
        hi = _as_number(expected[1])
        if lo is None or hi is None:
            return False
        return lo <= left <= hi
    raise ComparatorError(f"unknown hard-constraint op {op!r}", field="op")


def _baseline_value(baseline: dict[str, Any], name: str) -> Any:
    measurements = baseline.get("measurements")
    if isinstance(measurements, list):
        for item in measurements:
            if isinstance(item, dict) and item.get("name") == name:
                return item.get("value")
    if isinstance(measurements, dict) and name in measurements:
        return measurements[name]
    return None


def _margin_for(name: str, policy: dict[str, Any]) -> float:
    margins = policy.get("equivalence_margin") or {}
    if isinstance(margins, dict) and name in margins:
        return float(margins[name])
    if isinstance(margins, (int, float)):
        return float(margins)
    return 0.0


def _objective_delta(
    direction: str, candidate: float, reference: float, margin: float
) -> str:
    """Return better, worse, or equal relative to margin."""
    if direction == "minimize":
        if candidate < reference - margin:
            return "better"
        if candidate > reference + margin:
            return "worse"
        return "equal"
    if direction == "maximize":
        if candidate > reference + margin:
            return "better"
        if candidate < reference - margin:
            return "worse"
        return "equal"
    return "equal"


def compare(
    *,
    result: dict[str, Any],
    baseline: dict[str, Any],
    manifest: dict[str, Any],
) -> ComparisonResult:
    """Classify *result* against *baseline* using campaign comparator policy."""
    status = result.get("evaluator_status")
    if status in {"crash", "timeout"}:
        return ComparisonResult(
            comparator_outcome="invalid",
            trial_outcome="crashed",
            detail=f"evaluator_status={status}",
            advance_best=False,
        )
    if status != "success":
        return ComparisonResult(
            comparator_outcome="invalid",
            trial_outcome="invalid",
            detail=f"evaluator_status={status!r}",
            advance_best=False,
        )

    measurements = result.get("measurements")
    if not isinstance(measurements, dict):
        return ComparisonResult(
            "invalid", "invalid", "measurements missing or not an object", False
        )

    # Hard constraints first (from result records or recompute from manifest).
    hc_results = result.get("hard_constraint_results")
    if isinstance(hc_results, list) and hc_results:
        failed = [r for r in hc_results if isinstance(r, dict) and r.get("passed") is not True]
        if failed:
            names = ", ".join(str(r.get("name")) for r in failed)
            return ComparisonResult(
                "regresses",
                "rejected",
                f"hard constraint failed: {names}",
                False,
            )
    else:
        for constraint in manifest.get("hard_constraints") or []:
            if not isinstance(constraint, dict):
                continue
            name = constraint.get("name")
            measurement = constraint.get("measurement")
            op = constraint.get("op")
            expected = constraint.get("value")
            if not isinstance(measurement, str) or not isinstance(op, str):
                raise ComparatorError(
                    "hard constraint missing measurement or op",
                    field="hard_constraints",
                )
            actual = measurements.get(measurement)
            if actual is None:
                return ComparisonResult(
                    "invalid",
                    "invalid",
                    f"missing measurement for hard constraint {name!r}",
                    False,
                )
            if not _constraint_passed(op, actual, expected):
                return ComparisonResult(
                    "regresses",
                    "rejected",
                    f"hard constraint failed: {name}",
                    False,
                )

    policy = manifest.get("comparator_policy") or {}
    strategy = policy.get("strategy", "hard_constraints_then_objectives")
    if strategy == "human_review":
        return ComparisonResult(
            "inconclusive",
            "inconclusive",
            "strategy=human_review requires operator decision",
            False,
        )
    if strategy not in {"hard_constraints_then_objectives", "pareto"}:
        raise ComparatorError(
            f"unsupported comparator strategy {strategy!r}",
            field="comparator_policy.strategy",
        )

    replication = manifest.get("replication_policy") or {}
    min_repeats = int(replication.get("min_repeats") or 1)
    # Optional n on result; default 1.
    sample_n = result.get("sample_n")
    if sample_n is None:
        sample_n = 1
    if int(sample_n) < min_repeats:
        if not replication.get("single_noisy_run_advances_baseline", False):
            return ComparisonResult(
                "inconclusive",
                "inconclusive",
                f"sample_n={sample_n} < min_repeats={min_repeats}",
                False,
            )

    objectives = policy.get("objectives") or []
    if not objectives:
        raise ComparatorError("comparator_policy.objectives is empty", field="objectives")

    better = worse = equal = 0
    details: list[str] = []
    for obj in objectives:
        if not isinstance(obj, dict):
            continue
        name = obj.get("measurement")
        direction = obj.get("direction")
        if not isinstance(name, str) or not isinstance(direction, str):
            raise ComparatorError("objective missing measurement or direction")
        cand = measurements.get(name)
        ref = _baseline_value(baseline, name)
        if cand is None or ref is None:
            missing = "candidate" if cand is None else "baseline"
            return ComparisonResult(
                "invalid",
                "invalid",
                f"missing {missing} value for objective {name}",
                False,
            )
        cand_n = _as_number(cand)
        ref_n = _as_number(ref)
        if cand_n is None or ref_n is None:
            if cand == ref:
                equal += 1
                details.append(f"{name}=equal(non-numeric)")
                continue
            return ComparisonResult(
                "invalid",
                "invalid",
                f"non-numeric objective {name} cannot be ordered",
                False,
            )
        margin = _margin_for(name, policy)
        verdict = _objective_delta(direction, cand_n, ref_n, margin)
        details.append(f"{name}={verdict}")
        if verdict == "better":
            better += 1
        elif verdict == "worse":
            worse += 1
        else:
            equal += 1

    if better and not worse:
        outcome = "dominates"
    elif worse and not better:
        outcome = "regresses"
    elif better and worse:
        outcome = "mixed"
    else:
        outcome = "equivalent"

    trial = TRIAL_FROM_COMPARATOR[outcome]
    return ComparisonResult(
        comparator_outcome=outcome,
        trial_outcome=trial,
        detail="; ".join(details),
        advance_best=(outcome == "dominates"),
    )
