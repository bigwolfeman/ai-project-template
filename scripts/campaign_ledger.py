"""Ledger hash-chain, campaign-id, and pointer checks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from campaign_schema import SchemaError, SchemaStore, load_jsonl, validate_instance

POINTER_DIGEST = re.compile(r"^[a-f0-9]{64}$")
LAST_EVENT_STATE = {
    "campaign_created": "draft",
    "campaign_validated": "ready",
    "campaign_paused": "paused",
    "campaign_resumed": "running",
    "campaign_stopped": "stopped",
    "campaign_aborted": "aborted",
    "campaign_completed": "completed",
    "synthesis_recorded": "synthesized",
    "campaign_archived": "archived",
}
ID_FILES = (
    "evaluator.lock.json",
    "state/campaign.json",
    "state/baseline.json",
    "state/best.json",
)


def relerr(message: str, root: Path) -> str:
    prefix = str(root) + "/"
    if message.startswith(prefix):
        return message[len(prefix) :]
    return message


def check_ids_and_ledger(
    campaign_dir: Path, campaign_id: Any, store: SchemaStore, errors: Any, root: Path
) -> None:
    rel = campaign_dir.relative_to(root)
    for name in ID_FILES:
        path = campaign_dir / name
        if not path.is_file():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.add(f"{rel}/{name}: invalid JSON: {exc.msg}")
            continue
        if isinstance(doc, dict) and doc.get("campaign_id") != campaign_id:
            errors.add(
                f"{rel}/{name}: campaign_id: expected {campaign_id!r}, got {doc.get('campaign_id')!r}"
            )
    _check_ledger(campaign_dir, campaign_id, store, errors, root, rel)


def check_pointers(pointers: Path, rel: Path, errors: Any) -> None:
    if not pointers.is_dir():
        return
    allowed = {"path", "digest", "recorded_at", "media_type"}
    for path in sorted(pointers.glob("*.json")):
        loc = f"{rel}/pointers/{path.name}"
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.add(f"{loc}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(doc, dict):
            errors.add(f"{loc}: <root>: expected type object")
            continue
        for field in ("path", "digest", "recorded_at"):
            if field not in doc:
                errors.add(f"{loc}: {field}: missing required field")
        for field in sorted(set(doc) - allowed):
            errors.add(f"{loc}: {field}: unknown field")
        digest = doc.get("digest")
        if isinstance(digest, str) and POINTER_DIGEST.fullmatch(digest) is None:
            errors.add(f"{loc}: digest: expected sha256 hex")


def _check_ledger(
    campaign_dir: Path,
    campaign_id: Any,
    store: SchemaStore,
    errors: Any,
    root: Path,
    rel: Path,
) -> None:
    ledger_path = campaign_dir / "state" / "ledger.jsonl"
    if not ledger_path.is_file():
        return
    schema_path = store.schema_dir / "ledger-event.schema.json"
    schema = store.load(schema_path)
    try:
        rows = load_jsonl(ledger_path)
    except SchemaError as exc:
        errors.add(relerr(str(exc), root))
        return
    prev_raw: str | None = None
    last_type: str | None = None
    for raw, event in rows:
        for item in validate_instance(
            event, schema, source=str(ledger_path), schema_path=schema_path, store=store
        ):
            errors.add(relerr(item, root))
        if not isinstance(event, dict):
            continue
        if event.get("campaign_id") != campaign_id:
            errors.add(f"{rel}/state/ledger.jsonl: campaign_id: expected {campaign_id!r}")
        digest = event.get("prior_event_digest")
        if prev_raw is None:
            if digest is not None:
                errors.add(f"{rel}/state/ledger.jsonl: prior_event_digest: first event must be null")
        else:
            expected = hashlib.sha256(prev_raw.encode("utf-8")).hexdigest()
            if digest != expected:
                errors.add(f"{rel}/state/ledger.jsonl: prior_event_digest: expected {expected}")
        prev_raw = raw
        last_type = event.get("event_type")
    state_path = campaign_dir / "state" / "campaign.json"
    if not (last_type and state_path.is_file() and last_type in LAST_EVENT_STATE):
        return
    try:
        state_doc = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    expected_state = LAST_EVENT_STATE[last_type]
    if isinstance(state_doc, dict) and state_doc.get("state") != expected_state:
        errors.add(
            f"{rel}/state/campaign.json: state: expected {expected_state!r} after {last_type}"
        )
