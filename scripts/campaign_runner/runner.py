"""Orchestrate baseline and single-trial campaign runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import adapter_name_from_manifest, get_adapter
from .adapters.base import AdapterContext
from .budget import budget_from_ledger_events, check_budget, record_trial_resources
from .campaign_io import load_manifest, read_json, status_summary, validate_campaign
from .comparator import compare
from .env import assert_env_file_untouched, scrub_environ, snapshot_env_files
from .errors import (
    AdapterError,
    BudgetExhaustedError,
    LockMismatchError,
    ManifestError,
    ProcessTimeoutError,
)
from .isolation import (
    artifact_root,
    baseline_candidate_id,
    prepare_isolation,
    resolve_work_dir,
)
from .ledger_write import (
    append_event,
    read_ledger_events,
    rebuild_projections,
    write_baseline_measurements,
)
from .lock import load_lock, verify_lock

# Re-export for CLI and package __init__.
__all__ = [
    "run_baseline",
    "run_trial",
    "status_summary",
    "validate_campaign",
]


def run_baseline(campaign_dir: Path, *, adapter_name: str | None = None) -> dict[str, Any]:
    """Run the unchanged subject once; write baseline; append ledger."""
    campaign_dir = campaign_dir.resolve()
    validate_campaign(campaign_dir)
    manifest = load_manifest(campaign_dir)
    cid = str(manifest["campaign_id"])
    env_snap = snapshot_env_files(campaign_dir)
    prepare_isolation(campaign_dir, manifest, cid)

    lock_rel = str(manifest.get("evaluator_lock_path") or "evaluator.lock.json")
    lock = load_lock(campaign_dir / lock_rel)
    verify_lock(campaign_dir, lock, campaign_id=cid, when="before")

    events = read_ledger_events(campaign_dir)
    usage = budget_from_ledger_events(events)
    check_budget(manifest, usage, campaign_id=cid)

    trial_id = f"baseline-{len(events) + 1:04d}"
    candidate_id = baseline_candidate_id(campaign_dir)
    work_dir, cleanup = resolve_work_dir(campaign_dir, manifest, cid, trial_id)

    append_event(
        campaign_dir,
        event_type="baseline_started",
        campaign_id=cid,
        payload={"trial_id": trial_id, "candidate_id": candidate_id},
    )
    try:
        result_doc = _run_adapter(
            campaign_dir=campaign_dir,
            work_dir=work_dir,
            manifest=manifest,
            campaign_id=cid,
            trial_id=trial_id,
            candidate_id=candidate_id,
            adapter_name=adapter_name,
        )
        verify_lock(campaign_dir, lock, campaign_id=cid, when="after")
        measurements = result_doc.get("measurements")
        if not isinstance(measurements, dict):
            raise AdapterError("baseline result missing measurements", campaign_id=cid)
        write_baseline_measurements(
            campaign_dir,
            campaign_id=cid,
            candidate_id=candidate_id,
            measurements=measurements,
        )
        wall = float((result_doc.get("runtime_resource_use") or {}).get("wall_clock_seconds") or 0)
        record_trial_resources(usage, wall)
        append_event(
            campaign_dir,
            event_type="baseline_completed",
            campaign_id=cid,
            payload={"trial_id": trial_id, "candidate_id": candidate_id},
        )
        rebuild_projections(campaign_dir, campaign_id=cid)
        assert_env_file_untouched(campaign_dir, env_snap)
        return result_doc
    except (LockMismatchError, ProcessTimeoutError, AdapterError, BudgetExhaustedError):
        append_event(
            campaign_dir,
            event_type="campaign_aborted",
            campaign_id=cid,
            payload={"reason": "baseline_failed", "trial_id": trial_id},
        )
        rebuild_projections(campaign_dir, campaign_id=cid)
        raise
    finally:
        cleanup()


def run_trial(
    campaign_dir: Path,
    *,
    candidate_id: str,
    adapter_name: str | None = None,
) -> dict[str, Any]:
    """Verify lock, run adapter, compare, append ledger, update best if accepted."""
    campaign_dir = campaign_dir.resolve()
    if not candidate_id:
        raise ManifestError("candidate_id is required", field="candidate_id")
    validate_campaign(campaign_dir)
    manifest = load_manifest(campaign_dir)
    cid = str(manifest["campaign_id"])
    env_snap = snapshot_env_files(campaign_dir)
    prepare_isolation(campaign_dir, manifest, cid)

    baseline = read_json(campaign_dir / "state" / "baseline.json")
    if not baseline or not baseline.get("sealed"):
        raise ManifestError(
            "baseline is not sealed; run baseline first",
            campaign_id=cid,
            field="baseline.sealed",
        )

    lock_rel = str(manifest.get("evaluator_lock_path") or "evaluator.lock.json")
    lock = load_lock(campaign_dir / lock_rel)
    verify_lock(campaign_dir, lock, campaign_id=cid, when="before")

    events = read_ledger_events(campaign_dir)
    usage = budget_from_ledger_events(events)
    check_budget(manifest, usage, campaign_id=cid)

    trial_id = f"trial-{len(events) + 1:04d}"
    work_dir, cleanup = resolve_work_dir(campaign_dir, manifest, cid, trial_id)

    append_event(
        campaign_dir,
        event_type="trial_started",
        campaign_id=cid,
        payload={"trial_id": trial_id, "candidate_id": candidate_id},
    )
    try:
        result_doc = _run_adapter(
            campaign_dir=campaign_dir,
            work_dir=work_dir,
            manifest=manifest,
            campaign_id=cid,
            trial_id=trial_id,
            candidate_id=candidate_id,
            adapter_name=adapter_name,
        )
        verify_lock(campaign_dir, lock, campaign_id=cid, when="after")
        comparison = compare(result=result_doc, baseline=baseline, manifest=manifest)
        wall = float((result_doc.get("runtime_resource_use") or {}).get("wall_clock_seconds") or 0)
        record_trial_resources(usage, wall)

        event_type = "trial_crashed" if comparison.trial_outcome == "crashed" else "trial_completed"
        append_event(
            campaign_dir,
            event_type=event_type,
            campaign_id=cid,
            payload={
                "trial_id": trial_id,
                "candidate_id": candidate_id,
                "trial_outcome": comparison.trial_outcome,
                "comparator_outcome": comparison.comparator_outcome,
            },
        )
        disposition = {
            "accepted": "candidate_accepted",
            "rejected": "candidate_rejected",
            "invalid": "candidate_invalid",
            "inconclusive": "candidate_inconclusive",
            "crashed": "candidate_invalid",
        }[comparison.trial_outcome]
        append_event(
            campaign_dir,
            event_type=disposition,
            campaign_id=cid,
            payload={
                "trial_id": trial_id,
                "candidate_id": candidate_id,
                "trial_outcome": comparison.trial_outcome,
                "comparator_outcome": comparison.comparator_outcome,
                "reason": comparison.detail,
            },
        )
        if comparison.advance_best:
            append_event(
                campaign_dir,
                event_type="best_advanced",
                campaign_id=cid,
                payload={
                    "trial_id": trial_id,
                    "candidate_id": candidate_id,
                    "comparator_outcome": comparison.comparator_outcome,
                },
            )
        rebuild_projections(campaign_dir, campaign_id=cid)
        assert_env_file_untouched(campaign_dir, env_snap)
        return {
            "result": result_doc,
            "comparison": {
                "comparator_outcome": comparison.comparator_outcome,
                "trial_outcome": comparison.trial_outcome,
                "detail": comparison.detail,
                "advance_best": comparison.advance_best,
            },
        }
    except LockMismatchError:
        append_event(
            campaign_dir,
            event_type="campaign_aborted",
            campaign_id=cid,
            payload={"reason": "lock_mismatch", "trial_id": trial_id},
        )
        rebuild_projections(campaign_dir, campaign_id=cid)
        raise
    finally:
        cleanup()


def _run_adapter(
    *,
    campaign_dir: Path,
    work_dir: Path,
    manifest: dict[str, Any],
    campaign_id: str,
    trial_id: str,
    candidate_id: str,
    adapter_name: str | None,
) -> dict[str, Any]:
    name = adapter_name or adapter_name_from_manifest(manifest)
    adapter = get_adapter(name)
    timeout = None
    budget = manifest.get("resource_budget") or {}
    if isinstance(budget.get("max_wall_clock_seconds"), int):
        timeout = float(budget["max_wall_clock_seconds"])
    log_root = artifact_root(campaign_dir, manifest) / "logs" / trial_id
    ctx = AdapterContext(
        campaign_dir=campaign_dir,
        work_dir=work_dir,
        manifest=manifest,
        campaign_id=campaign_id,
        trial_id=trial_id,
        candidate_id=candidate_id,
        log_dir=log_root,
        timeout_seconds=timeout,
        env=scrub_environ(),
    )
    try:
        adapter.prepare(ctx)
        adapter.validate_candidate(ctx)
        proc = adapter.execute(ctx)
        raw = adapter.collect(ctx, proc)
        return adapter.normalize_result(raw, ctx)
    finally:
        adapter.cleanup(ctx)
