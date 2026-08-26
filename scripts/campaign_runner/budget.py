"""Track and enforce resource_budget and stop_conditions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import BudgetExhaustedError


@dataclass
class BudgetState:
    trial_count: int = 0
    wall_clock_seconds: float = 0.0
    consecutive_crashes: int = 0
    consecutive_rejected: int = 0
    stagnation_trials: int = 0
    cost: float = 0.0
    api_calls: int = 0
    compute_seconds: float = 0.0
    storage_bytes: int = 0
    stop_reason: str | None = None
    events_seen: list[str] = field(default_factory=list)


def budget_from_ledger_events(events: list[dict[str, Any]]) -> BudgetState:
    """Derive budget counters from ledger event types (bounded scan)."""
    state = BudgetState()
    for event in events:
        et = event.get("event_type")
        if not isinstance(et, str):
            continue
        state.events_seen.append(et)
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        if et in {"trial_completed", "trial_crashed", "baseline_completed"}:
            state.trial_count += 1
        if et == "trial_crashed":
            state.consecutive_crashes += 1
            state.consecutive_rejected = 0
            state.stagnation_trials += 1
        elif et == "trial_completed":
            outcome = payload.get("trial_outcome")
            if outcome == "crashed":
                state.consecutive_crashes += 1
                state.stagnation_trials += 1
            else:
                state.consecutive_crashes = 0
            if outcome == "rejected":
                state.consecutive_rejected += 1
                state.stagnation_trials += 1
            elif outcome == "accepted":
                state.consecutive_rejected = 0
                state.stagnation_trials = 0
            elif outcome in {"invalid", "inconclusive"}:
                state.stagnation_trials += 1
        elif et == "candidate_accepted":
            state.consecutive_rejected = 0
            state.stagnation_trials = 0
        elif et == "candidate_rejected":
            state.consecutive_rejected += 1
            state.stagnation_trials += 1
        elif et == "best_advanced":
            state.stagnation_trials = 0
    return state


def check_budget(
    manifest: dict[str, Any],
    usage: BudgetState,
    *,
    campaign_id: str | None = None,
    extra_wall_seconds: float = 0.0,
) -> None:
    """Raise BudgetExhaustedError when a limit or stop condition is hit."""
    budget = manifest.get("resource_budget") or {}
    if not isinstance(budget, dict):
        raise BudgetExhaustedError(
            "resource_budget missing",
            campaign_id=campaign_id,
            field="resource_budget",
        )

    def _hit(reason: str, field: str) -> None:
        usage.stop_reason = reason
        raise BudgetExhaustedError(
            reason,
            campaign_id=campaign_id,
            field=field,
        )

    max_trials = budget.get("max_trial_count")
    if isinstance(max_trials, int) and usage.trial_count >= max_trials:
        _hit(f"max_trial_count reached ({max_trials})", "max_trial_count")

    max_wall = budget.get("max_wall_clock_seconds")
    wall = usage.wall_clock_seconds + extra_wall_seconds
    if isinstance(max_wall, int) and wall >= max_wall:
        _hit(f"max_wall_clock_seconds reached ({max_wall})", "max_wall_clock_seconds")

    max_crashes = budget.get("max_consecutive_crashes")
    if isinstance(max_crashes, int) and usage.consecutive_crashes >= max_crashes:
        _hit(
            f"max_consecutive_crashes reached ({max_crashes})",
            "max_consecutive_crashes",
        )

    max_rejected = budget.get("max_consecutive_rejected")
    if isinstance(max_rejected, int) and usage.consecutive_rejected >= max_rejected:
        _hit(
            f"max_consecutive_rejected reached ({max_rejected})",
            "max_consecutive_rejected",
        )

    max_stag = budget.get("max_stagnation_trials")
    if isinstance(max_stag, int) and usage.stagnation_trials >= max_stag:
        _hit(
            f"max_stagnation_trials reached ({max_stag})",
            "max_stagnation_trials",
        )

    for key, attr in (
        ("max_cost", "cost"),
        ("max_api_calls", "api_calls"),
        ("max_compute_seconds", "compute_seconds"),
        ("max_storage_bytes", "storage_bytes"),
    ):
        limit = budget.get(key)
        value = getattr(usage, attr)
        if limit is not None and value >= limit:
            _hit(f"{key} reached ({limit})", key)

    stops = manifest.get("stop_conditions") or []
    for cond in stops:
        if not isinstance(cond, dict):
            continue
        ctype = cond.get("type")
        threshold = cond.get("threshold")
        if ctype == "budget_exhausted":
            # Already enforced via resource_budget fields above.
            continue
        if ctype == "max_trials" and isinstance(max_trials, int):
            if usage.trial_count >= (threshold or max_trials):
                _hit("stop_condition max_trials", "stop_conditions")
        if ctype == "stagnation" and isinstance(threshold, int):
            if usage.stagnation_trials >= threshold:
                _hit("stop_condition stagnation", "stop_conditions")
        if ctype == "consecutive_crashes" and isinstance(threshold, int):
            if usage.consecutive_crashes >= threshold:
                _hit("stop_condition consecutive_crashes", "stop_conditions")
        if ctype == "consecutive_rejected" and isinstance(threshold, int):
            if usage.consecutive_rejected >= threshold:
                _hit("stop_condition consecutive_rejected", "stop_conditions")


def record_trial_resources(usage: BudgetState, wall_clock_seconds: float) -> None:
    usage.wall_clock_seconds += max(0.0, wall_clock_seconds)
