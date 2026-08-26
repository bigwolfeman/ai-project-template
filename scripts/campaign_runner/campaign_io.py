"""Load and validate campaign manifests; status summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from campaign_schema import ROOT, load_document
from verify_campaign import _check_campaign_dir

from .budget import budget_from_ledger_events
from .errors import ManifestError, ValidationError
from .ledger_write import read_ledger_events


class Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)


def load_manifest(campaign_dir: Path) -> dict[str, Any]:
    path = campaign_dir / "campaign.yaml"
    if not path.is_file():
        raise ManifestError("missing campaign.yaml", path=str(path))
    try:
        doc = load_document(path)
    except (OSError, ValueError) as exc:
        raise ManifestError(str(exc), path=str(path)) from exc
    if not isinstance(doc, dict):
        raise ManifestError("campaign.yaml root must be an object", path=str(path))
    return doc


def validate_campaign(campaign_dir: Path, *, root: Path = ROOT) -> None:
    """Schema + lock presence. Raises ValidationError on failure."""
    errors = Errors()
    _check_campaign_dir(campaign_dir.resolve(), errors, root=root)
    lock_path = campaign_dir / "evaluator.lock.json"
    if not lock_path.is_file():
        errors.add(f"{campaign_dir}/evaluator.lock.json: missing")
    if errors.items:
        raise ValidationError("campaign validation failed:\n  - " + "\n  - ".join(errors.items))


def status_summary(campaign_dir: Path) -> str:
    manifest = load_manifest(campaign_dir)
    cid = str(manifest.get("campaign_id"))
    state_doc = read_json(campaign_dir / "state" / "campaign.json")
    baseline = read_json(campaign_dir / "state" / "baseline.json")
    best = read_json(campaign_dir / "state" / "best.json")
    events = read_ledger_events(campaign_dir)
    usage = budget_from_ledger_events(events)
    lines = [
        f"campaign_id: {cid}",
        f"state: {state_doc.get('state') if state_doc else 'unknown'}",
        f"baseline_sealed: {baseline.get('sealed') if baseline else False}",
        f"baseline_candidate: {baseline.get('candidate_id') if baseline else None}",
        f"best_candidate: {best.get('candidate_id') if best else None}",
        f"ledger_events: {len(events)}",
        f"trial_count: {usage.trial_count}",
        f"consecutive_crashes: {usage.consecutive_crashes}",
        f"stagnation_trials: {usage.stagnation_trials}",
    ]
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON: {exc.msg}", path=str(path)) from exc
    return doc if isinstance(doc, dict) else None
