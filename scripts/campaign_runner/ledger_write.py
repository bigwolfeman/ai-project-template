"""Append JSONL ledger events with prior-event digest; rebuild projections."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from campaign_ledger import LAST_EVENT_STATE
from campaign_schema import SchemaStore, validate_instance

from .errors import LedgerError

SCHEMA_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ledger_path(campaign_dir: Path) -> Path:
    return campaign_dir / "state" / "ledger.jsonl"


def read_ledger_raw_lines(campaign_dir: Path) -> list[str]:
    path = _ledger_path(campaign_dir)
    if not path.is_file():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            lines.append(raw)
    return lines


def read_ledger_events(campaign_dir: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw in read_ledger_raw_lines(campaign_dir):
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LedgerError(
                f"invalid JSON in ledger: {exc.msg}",
                path=str(_ledger_path(campaign_dir)),
            ) from exc
        if not isinstance(doc, dict):
            raise LedgerError("ledger event must be an object", path=str(_ledger_path(campaign_dir)))
        events.append(doc)
    return events


def prior_digest_for_append(campaign_dir: Path) -> str | None:
    lines = read_ledger_raw_lines(campaign_dir)
    if not lines:
        return None
    return hashlib.sha256(lines[-1].encode("utf-8")).hexdigest()


def append_event(
    campaign_dir: Path,
    *,
    event_type: str,
    campaign_id: str,
    actor: str = "runner",
    payload: dict[str, Any] | None = None,
    event_id: str | None = None,
    timestamp: str | None = None,
    validate: bool = True,
    schema_dir: Path | None = None,
) -> dict[str, Any]:
    """Append one event. Returns the written event object."""
    state_dir = campaign_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _ledger_path(campaign_dir)
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id or f"evt-{uuid.uuid4().hex[:12]}",
        "event_type": event_type,
        "campaign_id": campaign_id,
        "timestamp": timestamp or _utc_now(),
        "actor": actor,
        "prior_event_digest": prior_digest_for_append(campaign_dir),
        "payload": payload or {},
    }
    if validate:
        root = campaign_dir
        # Walk up to repo schemas when possible.
        store_dir = schema_dir
        if store_dir is None:
            for parent in [campaign_dir, *campaign_dir.parents]:
                candidate = parent / "schemas"
                if candidate.is_dir():
                    store_dir = candidate
                    break
        if store_dir is not None:
            store = SchemaStore(store_dir)
            schema_path = store_dir / "ledger-event.schema.json"
            errors = validate_instance(
                event, store.load(schema_path), source="ledger", schema_path=schema_path, store=store
            )
            if errors:
                raise LedgerError(
                    "ledger event failed schema: " + "; ".join(errors),
                    campaign_id=campaign_id,
                    field="payload",
                )

    line = json.dumps(event, separators=(",", ":"), sort_keys=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return event


def rebuild_projections(campaign_dir: Path, *, campaign_id: str | None = None) -> None:
    """Rebuild campaign.json, baseline.json, best.json from the ledger."""
    events = read_ledger_events(campaign_dir)
    if not events and campaign_id is None:
        raise LedgerError("empty ledger and no campaign_id", path=str(campaign_dir))

    cid = campaign_id or str(events[0].get("campaign_id"))
    state = "draft"
    updated_at = _utc_now()
    stop_reason: str | None = None
    baseline_id: str | None = None
    best_candidate_id: str | None = None
    baseline_sealed = False
    baseline_established: str | None = None
    best_source = "none"
    best_advanced_at: str | None = None
    best_trial_id: str | None = None

    baseline_path = campaign_dir / "state" / "baseline.json"
    existing_measurements: list[Any] = []
    if baseline_path.is_file():
        try:
            prior = json.loads(baseline_path.read_text(encoding="utf-8"))
            if isinstance(prior, dict) and isinstance(prior.get("measurements"), list):
                existing_measurements = prior["measurements"]
        except json.JSONDecodeError:
            existing_measurements = []

    for event in events:
        et = event.get("event_type")
        ts = event.get("timestamp")
        if isinstance(ts, str):
            updated_at = ts
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        if isinstance(et, str) and et in LAST_EVENT_STATE:
            state = LAST_EVENT_STATE[et]
            if et in {"campaign_stopped", "campaign_aborted"}:
                stop_reason = payload.get("stop_condition") or payload.get("reason")
        if et == "baseline_completed":
            baseline_id = payload.get("candidate_id") or baseline_id or "baseline"
            baseline_sealed = True
            baseline_established = updated_at
            if best_candidate_id is None:
                best_candidate_id = baseline_id
                best_source = "baseline"
                best_advanced_at = updated_at
        if et == "best_advanced":
            best_candidate_id = payload.get("candidate_id") or best_candidate_id
            best_source = "accepted_trial"
            best_advanced_at = updated_at
            best_trial_id = payload.get("trial_id")
        if et == "candidate_accepted" and best_candidate_id is None:
            best_candidate_id = payload.get("candidate_id")

    campaign_doc = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": cid,
        "state": state,
        "updated_at": updated_at,
        "stop_reason": stop_reason,
        "baseline_id": baseline_id,
        "best_candidate_id": best_candidate_id,
    }
    baseline_doc = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": cid,
        "sealed": baseline_sealed,
        "candidate_id": baseline_id,
        "established_at": baseline_established,
        "measurements": existing_measurements if baseline_sealed else [],
        "uncertainty_note": None,
    }
    best_doc = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": cid,
        "candidate_id": best_candidate_id,
        "source": best_source if best_candidate_id else "none",
        "advanced_at": best_advanced_at,
        "trial_id": best_trial_id,
    }
    state_dir = campaign_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "campaign.json").write_text(
        json.dumps(campaign_doc, indent=2) + "\n", encoding="utf-8"
    )
    (state_dir / "baseline.json").write_text(
        json.dumps(baseline_doc, indent=2) + "\n", encoding="utf-8"
    )
    (state_dir / "best.json").write_text(
        json.dumps(best_doc, indent=2) + "\n", encoding="utf-8"
    )


def write_baseline_measurements(
    campaign_dir: Path,
    *,
    campaign_id: str,
    candidate_id: str,
    measurements: dict[str, Any],
    established_at: str | None = None,
) -> None:
    """Write sealed baseline projection including measurement values."""
    items = [{"name": name, "value": value} for name, value in measurements.items()]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": campaign_id,
        "sealed": True,
        "candidate_id": candidate_id,
        "established_at": established_at or _utc_now(),
        "measurements": items,
        "uncertainty_note": None,
    }
    path = campaign_dir / "state" / "baseline.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
